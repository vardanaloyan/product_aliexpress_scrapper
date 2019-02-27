#!/usr/bin/env python
import json
import pickle
from datetime import datetime
from bs4 import BeautifulSoup
import bs4
import sys ,os,re, csv
import requests

import io

# from selenium import webdriver

headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'
    }
def extract_product_info(product_url, write_csv = False):
    session = requests.Session()
    session.max_redirects = 9999999
    page = session.get(product_url, headers=headers, verify=False)
    content = page.content

    # browser = webdriver.PhantomJS()
    # browser.get(product_url)
    # # content = browser.page_source
    # content = browser.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
    # with io.open("resp.html", "w", encoding="utf-8") as r:
    #     r.write(content)
    # with open("resp.html", "w") as r:
    #     r.write(content)

        # window.runParams.detailDesc=
    soup = BeautifulSoup(content, "html.parser")

    scripts = soup.find_all("script")

    s = ""
    var1 = "window.runParams.detailDesc="
    for i in scripts:
            if var1 in i.text:
                s = i.text
    # print script
    
    _t = s[s.find(var1)+len(var1):]
    desc_url = _t[:_t.find(';')].strip().replace('\t','').replace('\n','')
    desc_urls = parse_desc(desc_url)
    # print desc_urls
    # tmp = s[s.find("[")+1:s.find("]")].strip().replace('\t','').replace('\n','')
    # print tmp

    # desc_url = script[script.find("window.runParams.detailDesc=")+1:script[script.find("window.runParams.detailDesc=")+1:].find(";")].strip().replace('\t','').replace('\n','')
    # print desc_url

    product_id = soup.find('input', {'id': 'hid-product-id'})['value']
    # print "product-> ", product_id
    title = soup.find('h1', {'class': 'product-name'}).text
#    print title
    price= soup.find('span', {'id': 'j-sku-price', 'class': 'p-price'}).text
#    price = float(soup.find('span', {'id': 'j-sku-price'}).text.split('-')[0])
#    print price
    if soup.find('span', {'id': 'j-sku-discount-price'}):
        discount_price = soup.find('span', {'id': 'j-sku-discount-price'}).text
    else:
        discount_price = None
#    print discount_price
    properties = soup.findAll('li', {'class': 'property-item'})
    attrs_dict = {}
    for item in properties:
        # print item
        name = item.find('span', {'class': 'propery-title'}).text[:-1]
        val = item.find('span', {'class': 'propery-des'}).text
        attrs_dict[name] = val
    description = json.dumps(attrs_dict)

    # stars = float(soup.find('span', {'class': 'percent-num'}).text)
    # votes = int(soup.find('span', {'itemprop': 'reviewCount'}).text)
    # orders = int(soup.find('span', {'id': 'j-order-num'}).text.split()[0].replace(',', ''))
    # wishlists = 0  # int(soup.find('span', {'id': 'j-wishlist-num'}).text.strip()[1:-1].split()[0])

    # try:
    #     shipping_cost = soup.find('span', {'class': 'logistics-cost'}).text
    #     shipping_company = soup.find('span', {'id': 'j-shipping-company'}).text
    # except Exception:
    #     shipping_cost = ''
    #     shipping_company = ''
    # is_free_shipping = shipping_cost == 'Free Shipping'
    # is_epacket = shipping_company == 'ePacket'

    primary_image_url = soup.find('div', {'id': 'magnifier'}).find('img')['src']

    # store_id = soup.find('span', {'class': 'store-number'}).text.split('.')[-1]
    # store_name = soup.find('span', {'class': 'shop-name'}).find('a').text
    # store_start_date = soup.find('span', {'class': 'store-time'}).find('em').text
    # store_start_date = datetime.strptime(store_start_date, '%b %d, %Y')

    # if soup.find('span', {'class': 'rank-num'}):
    #     store_feedback_score = int(soup.find('span', {'class': 'rank-num'}).text)
    #     store_positive_feedback_rate = float(soup.find('span', {'class': 'positive-percent'}).text[:-1]) * 0.01
    # else:
    #     try:
    #         store_feedback_score = int(soup.find('span', {'class': 'rank-num'}).text)
    #         store_positive_feedback_rate = float(soup.find('span', {'class': 'positive-percent'}).text[:-1]) * 0.01
    #     except Exception:
    #         store_feedback_score = -1
    #         store_positive_feedback_rate = -1

    category = ""
    subcategory1 = ""
    subcategory2 = ""

    try:
        cats = [item.text for item in soup.find('div', {'class': 'ui-breadcrumb'}).findAll('a')]
        # category = '||'.join(cats)
    except Exception:
        # category = ''
        cats = []

    if len(cats) > 2:
        category = cats[2]

        for i, sub in enumerate(cats[3:]):
            if i == 0:
                subcategory1 = sub
            elif i == 1:
                subcategory2 = sub

    try:
        colors = [i['title'] for i in soup.find('ul', {'id': 'j-sku-list-1'}).findAll('a') if isinstance(i, bs4.element.Tag)]
    except:
        colors = []
    try:
        sizes =  [i.find('span').text for i in soup.find('ul', {'id': 'j-sku-list-2'}).findAll('a')]
    except: 
        sizes = []

    main_images = soup.find('div', {'id': 'j-detail-gallery-main'}).findAll('script')

    # regex_string = '{parameter}= "(.*?)"'.format(parameter='window.runParams.mainBigPic ')
    # print re.findall(regex_string, i.text)

    s=main_images[-1].text
    image_urls = s[s.find("[")+1:s.find("]")].strip().replace('\t','').replace('\n','')
    
    if len(colors) or len(sizes):
        productType = "variable"
    else:
        productType = "single"



    row = {
        'product_id': product_id,
        'name': title,
        'description_text': eval(description),
        'price': price,
        'discount_price': discount_price,
        'colors': colors,
        'sizes': sizes,
        'productType': productType,
        'image_urls': image_urls,
        'desc_images' : desc_urls,
#        'stars': stars,
#        'votes': votes,
#        'orders': orders,
#        'wishlists': wishlists,
#        'is_free_shipping': is_free_shipping,
#        'is_epacket': is_epacket,
        'primary_image_url': primary_image_url,
#        'store_id': store_id,
#        'store_name': store_name,
#        'store_start_date': store_start_date,
#        'store_feedback_score': store_feedback_score,
#        'store_positive_feedback_rate': store_positive_feedback_rate,
        'category': category,
        'subcategory1': subcategory1,
        'subcategory2': subcategory2,
        'product_url': product_url
    }

    fields = ['product_url', 'product_id', 'name', 'price', 'discount_price', 'category', 'subcategory1', 'subcategory2', 'colors', 'sizes', 'productType', 'description_text', 'primary_image_url', 'image_urls', 'desc_images']

    if write_csv:
        with open('basic_%s.csv' % product_id, 'w', encoding="utf-8") as f:
            writer = csv.DictWriter(f, fields)
            writer.writeheader()
            writer.writerow(row)

    print ("BASIC: {}\t1/1".format(product_id))
    return fields, row


def parse_desc(url):
    session = requests.Session()
    session.max_redirects = 9999999
    url = url.strip('"')
    page = session.get(url,headers=headers, verify=False)
    content = page.content
    soup = BeautifulSoup(content, "html.parser")
    imgs = [i['src'] for i in soup.find_all("img")]
    return imgs


if __name__ == '__main__':
    url = "https://ru.aliexpress.com/store/product/Balabala-baby-girls-clothing-set-newborn-100-cotton-lovely-printed-clothes-suit-short-sleeve-t-shirt/3218069_32859893411.html?spm=a2g0v.12010612.8148356.1.4bf563b3NjjNzs"
    out = extract_product_info(url, write_csv = True)
    print(out[1]["product_id"])
