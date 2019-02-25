import csv
import requests


def extract_product_shipping(product_id, max_page=200):
    url_template = 'https://freight.aliexpress.com/ajaxFreightCalculateService.htm?callback=jQuery1830650128321702308_1551079034704&f=d&productid={product_id}&count=1&minPrice=5.30&maxPrice=5.30&currencyCode={currencyCode}&transactionCurrencyCode={transactionCurrencyCode}&sendGoodsCountry=&country={country}&province=&city=&abVersion=1&_=1551080238699'
    currencyCode = "USD"
    transactionCurrencyCode = "USD"
    country = "GR"
    initial_url = url_template.format(product_id = product_id, currencyCode = currencyCode, transactionCurrencyCode=transactionCurrencyCode, country = country)
    shippings = []

    s = requests.Session()

    resp = s.get(initial_url)
    if resp.status_code == 200:
        data = resp.content.split('(')[1].strip(')')
        false = "false"
        true = "true"
        null = "null"
        data = eval(data)
        data = data["freight"]
        for dct in data:
#            print 'country: ', country, ', company: ', dct['companyDisplayName'], ', EstimatedTime: ', dct['time'], ', cost: ', dct['price'], ', tracked: ',dct['isTracked']
            temp_dct = dict(productid = product_id, country = country, company = dct['companyDisplayName'],  cost = dct['price']+ ' %s' %currencyCode, estimatedTime = dct['time'] + ' days', tracked = dct['isTracked'])
            keys = ['productid', 'country', 'company', 'cost', 'estimatedTime', 'tracked']
            shippings.append(temp_dct)

        itr = 0
        with open('sheepings.csv', 'w') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            if itr == 0:
                dict_writer.writeheader()
                itr += 1
            dict_writer.writerows(shippings)
        # print dct
#        data = resp.json()
#        print data.keys()
    #     total_page = data['totalPage']
    #     print (data.keys())
    #     print (data['totalNum'])
    #     print (total_page)
    #     total_page = min([total_page, max_page])
    #     reviews += data['evaViewList']

    #     if total_page > 1:
    #         next_page = 2
    #         while next_page <= total_page:
    #             print('{}\t{}/{}'.format(product_id, next_page, total_page))
    #             next_url = url_template.format(next_page, product_id)
    #             resp = s.get(next_url)

    #             next_page += 1

    #             try:
    #                 data = resp.json()
    #             except Exception:
    #                 continue

    #             reviews += data['evaViewList']

    # filtered_reviews = []
    # for review in reviews:
    #     data = {
    #         'anonymous': review['anonymous'],
    #         'buyerCountry': review['buyerCountry'],
    #         'buyerEval': review['buyerEval'],
    #         'buyerFeedback': review['buyerFeedback'],
    #         'buyerGender': review['buyerGender'] if 'buyerGender' in review else '',
    #         'buyerHeadPortrait': review['buyerHeadPortrait'] if 'buyerHeadPortrait' in review else '',
    #         'buyerId': review['buyerId'] if 'buyerId' in review else '',
    #         'buyerName': review['buyerName'],
    #         'evalDate': review['evalDate'],
    #         'image': review['images'][0] if 'images' in review and len(review['images']) > 0 else '',
    #         'logistics': review['logistics'] if 'logistics' in review else '',
    #         'skuInfo': review['skuInfo'] if 'skuInfo' in review else '',
    #         'thumbnail': review['thumbnails'][0] if 'thumbnails' in review and len(review['thumbnails']) > 0 else '',
    #     }
    #     filtered_reviews.append(data)

    # keys = filtered_reviews[0].keys()
    # with open('reviews.csv', 'w') as output_file:
    #     dict_writer = csv.DictWriter(output_file, keys)
    #     dict_writer.writeheader()
    #     dict_writer.writerows(filtered_reviews)
    # return filtered_reviews


if __name__ == '__main__':
    extract_product_shipping('32868589524')

