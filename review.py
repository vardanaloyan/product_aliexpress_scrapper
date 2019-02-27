import csv
import requests


def extract_product_reviews(product_id, max_page=2000, write_csv = False):
    # url_template = 'https://m.aliexpress.com/ajaxapi/EvaluationSearchAjax.do?type=all&index={}&pageSize=20&productId={}' #&country=EC
    # initial_url = url_template.format(1, product_id)
    url_template = 'https://m.aliexpress.com/ajaxapi/EvaluationSearchAjax.do?type=all&index={}&pageSize=20&productId={}' #&country=EC
    initial_url = url_template.format(1, product_id)
    reviews = []
    s = requests.Session()
    resp = s.get(initial_url)
    if resp.status_code == 200:
        data = resp.json()
        total_page = data['totalPage']
        total_page = min([total_page, max_page])
        reviews += data['evaViewList']
        print('REVIEW: {}\t{}/{}'.format(product_id, 1, total_page))

        if total_page > 1:
            next_page = 2
            while next_page <= total_page:
                print('REVIEW: {}\t{}/{}'.format(product_id, next_page, total_page))
                next_url = url_template.format(next_page, product_id)
                resp = s.get(next_url)

                next_page += 1

                try:
                    data = resp.json()
                except Exception:
                    continue

                reviews += data['evaViewList']

    filtered_reviews = []
    for review in reviews:

        data = {
            'productId': product_id,
            'anonymous': review['anonymous'],
            'buyerCountry': review['buyerCountry'],
            'buyerEval': review['buyerEval'],
            'buyerFeedback': review['buyerFeedback'],
            'buyerGender': review['buyerGender'] if 'buyerGender' in review else '',
            'buyerHeadPortrait': review['buyerHeadPortrait'] if 'buyerHeadPortrait' in review else '',
            'buyerId': review['buyerId'] if 'buyerId' in review else '',
            'buyerName': review['buyerName'],
            'evalDate': review['evalDate'],
            'images': review['images'] if 'images' in review and len(review['images']) > 0 else '',
            'logistics': review['logistics'] if 'logistics' in review else '',
            'skuInfo': review['skuInfo'] if 'skuInfo' in review else '',
            'thumbnail': review['thumbnails'] if 'thumbnails' in review and len(review['thumbnails']) > 0 else '',
        }
        filtered_reviews.append(data)

    # keys = filtered_reviews[0].keys()
    keys = ['productId', 'buyerId', 'buyerName', 'buyerEval', 'buyerFeedback', 'buyerCountry', 'buyerGender', \
    'buyerHeadPortrait', "evalDate", "anonymous", "images", "logistics", "thumbnail", "skuInfo"]

    if write_csv:
        with open('reviews_%s.csv' % product_id, 'w') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(filtered_reviews)

    return keys, filtered_reviews


if __name__ == '__main__':
    extract_product_reviews('32859893411', write_csv = True)

