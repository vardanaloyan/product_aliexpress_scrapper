#!/usr/bin/env python
#
import json
import pickle
from datetime import datetime
from bs4 import BeautifulSoup
import sys ,os,re, csv
import requests
headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'
    }
def extract_product_info(product_url):
    session = requests.Session()
    session.max_redirects = 9999999
    page = session.get(product_url,headers=headers, verify=False)
    content = page.content

    soup = BeautifulSoup(content, "html.parser")

    product_id = soup.find('input', {'id': 'hid-product-id'})['value']
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
        name = item.find('span', {'class': 'propery-title'}).text[:-1]
        val = item.find('span', {'class': 'propery-des'}).text
        attrs_dict[name] = val
    description = json.dumps(attrs_dict)

    stars = float(soup.find('span', {'class': 'percent-num'}).text)
    votes = int(soup.find('span', {'itemprop': 'reviewCount'}).text)
    orders = int(soup.find('span', {'id': 'j-order-num'}).text.split()[0].replace(',', ''))
    wishlists = 0  # int(soup.find('span', {'id': 'j-wishlist-num'}).text.strip()[1:-1].split()[0])

    try:
        shipping_cost = soup.find('span', {'class': 'logistics-cost'}).text
        shipping_company = soup.find('span', {'id': 'j-shipping-company'}).text
    except Exception:
        shipping_cost = ''
        shipping_company = ''
    is_free_shipping = shipping_cost == 'Free Shipping'
    is_epacket = shipping_company == 'ePacket'

    primary_image_url = soup.find('div', {'id': 'magnifier'}).find('img')['src']

    store_id = soup.find('span', {'class': 'store-number'}).text.split('.')[-1]
    store_name = soup.find('span', {'class': 'shop-name'}).find('a').text
    store_start_date = soup.find('span', {'class': 'store-time'}).find('em').text
    store_start_date = datetime.strptime(store_start_date, '%b %d, %Y')

    if soup.find('span', {'class': 'rank-num'}):
        store_feedback_score = int(soup.find('span', {'class': 'rank-num'}).text)
        store_positive_feedback_rate = float(soup.find('span', {'class': 'positive-percent'}).text[:-1]) * 0.01
    else:
        try:
            store_feedback_score = int(soup.find('span', {'class': 'rank-num'}).text)
            store_positive_feedback_rate = float(soup.find('span', {'class': 'positive-percent'}).text[:-1]) * 0.01
        except Exception:
            store_feedback_score = -1
            store_positive_feedback_rate = -1

    try:
        cats = [item.text for item in soup.find('div', {'class': 'ui-breadcrumb'}).findAll('a')]
        category = '||'.join(cats)
    except Exception:
        category = ''

    row = {
        'product_id': product_id,
        'name': title,
        'description_text': eval(description),
        'price': price,
        'discount_price': discount_price,
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
        'product_url': product_url
    }
    return row


if __name__ == '__main__':
    out = extract_product_info('https://ru.aliexpress.com/item/2016-nuevos-hombres-Ciclismo-Ciclismo-Gafas-Sunglass-Gafas-al-aire-libre-para-bicicleta-Deportes-UV400-Gafas/32595591034.html?spm=2114.33020108.8.27.3a0e7bKp7bKpaP&amp%3Bpvid=6accd090-ba0c-439e-a795-32777984f763&amp%3Bscm=1007.17258.123254.0')
#    for i in out:
#	print i,": ",out[i]
    #fields = list(out.keys())
    # 'colors', 'sizes', 'product_type', 'description_images', 'subcategory1', 'subcategory2', 'subcategory3', 'image_urls'
    #print (str(eval(out['description_text'])))
    fields = ['product_url', 'product_id', 'name', 'price', 'discount_price', 'category', 'description_text', 'primary_image_url']
#    fields = ['description', 'wishlists', 'category', 'is_epacket', 'product_id', 'store_name', 'orders', 'store_id', 'product_url', 'store_start_date', 'discount_price', 'store_feedback_score', 'is_free_shipping', 'price', 'votes', 'store_positive_feedback_rate', 'stars', 'primary_image_url', 'title']
    with open('basic.csv', 'a', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fields)
        writer.writeheader()
        writer.writerow(out)
