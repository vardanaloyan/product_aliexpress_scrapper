import csv
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

shipping_country_codes =     ['AR', 'AT', 'AU', 'BE', 'BR', 'CA', 'CH', 'CL', 'CZ', 'DE', 'DK',
                              'ES', 'FI', 'FR', 'GB', 'IE', 'IL', 'IN', 'IT', 'MX', 'NL', 'NO',
                              'NZ', 'PL', 'PT', 'RU', 'SE', 'SK', 'TR', 'US', 'AG', 'AO', 'AW',
                              'DZ', 'AI', 'AQ', 'AX', 'AS', 'AF', 'AL', 'AD', 'AM', 'BM', 'BG',
                              'BQ', 'BI', 'TD', 'BW', 'BS', 'BT', 'KH', 'BZ', 'BF', 'BA', 'BN',
                              'BY', 'AZ', 'BD', 'BB', 'BV', 'IO', 'CV', 'CF', 'CM', 'KY', 'BJ',
                              'BO', 'BH', 'CX', 'CK', 'GF', 'DJ', 'CI', 'CU', 'CY', 'CR', 'CW',
                              'EC', 'FK', 'CC', 'EE', 'FO', 'CN', 'CO', 'CD', 'DO', 'FJ', 'SV',
                              'GQ', 'HR', 'DM', 'KM', 'ET', 'CG', 'EG', 'ER', 'GG', 'GY', 'GL',
                              'GD', 'GU', 'ID', 'GM', 'HT', 'HM', 'GW', 'IS', 'GI', 'GN', 'GE',
                              'GR', 'GH', 'VA', 'HK', 'GA', 'TF', 'HU', 'PF', 'GP', 'HN', 'GT',
                              'KI', 'KP', 'IQ', 'IR', 'KP', 'IR', 'MT', 'MR', 'MM', 'MW', 'MV',
                              'MU', 'MC', 'MZ', 'YT', 'NR', 'MD', 'ME', 'LS', 'MO', 'MQ', 'NC',
                              'KW', 'LV', 'MG', 'MN', 'MH', 'MS', 'NP', 'LU', 'LB', 'MY', 'NA',
                              'LI', 'LT', 'ML', 'FM', 'KG', 'LY', 'MK', 'MA', 'PH', 'PG', 'PE',
                              'PN', 'PS', 'RE', 'NE', 'NI', 'PR', 'QA', 'PA', 'NG', 'PY', 'MP',
                              'OM', 'PK', 'PW', 'NU', 'NF', 'RO', 'SH', 'LC', 'SI', 'KN', 'SN',
                              'SX', 'SB', 'GS', 'WS', 'SC', 'SA', 'SO', 'ST', 'BL', 'SM', 'SL',
                              'MF', 'RW', 'PM', 'RS', 'VC', 'SG', 'ZA', 'SZ', 'SY', 'TZ', 'LK',
                              'SR', 'TH', 'SJ', 'TW', 'TJ', 'SD', 'TM', 'TG', 'TO', 'TL', 'UA',
                              'TT', 'TN', 'TC', 'TK', 'UG', 'TV', 'AE', 'VU', 'VE', 'UY', 'UM',
                              'UZ', 'VN', 'YE', 'VG', 'EH', 'ZM', 'WF', 'VI', 'ZW', 'LR']

def Extract(product_id, max_page=2000, write_csv = False):
    reviews = []
    keys = ['productId', 'buyerId', 'buyerName', 'buyerEval', 'buyerFeedback', 'buyerCountry', 'buyerGender', \
    'buyerHeadPortrait', "evalDate", "anonymous", "images", "logistics", "thumbnail", "skuInfo"]
    for country in shipping_country_codes:
        reviews += extract_product_reviews(product_id, country=country, max_page=max_page, write_csv=write_csv)

    if write_csv:
        with open('reviews_%s.csv' % product_id, 'w') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(filtered_reviews)

    return keys, reviews

def extract_product_reviews(product_id, country = "US", max_page=2000, write_csv = False):
    # url_template = 'https://m.aliexpress.com/ajaxapi/EvaluationSearchAjax.do?type=all&index={}&pageSize=20&productId={}' #&country=EC
    # initial_url = url_template.format(1, product_id)
    url_template = 'https://m.aliexpress.com/ajaxapi/EvaluationSearchAjax.do?type=all&index={}&pageSize=20&productId={}&country={}' #&country=EC
    initial_url = url_template.format(1, product_id, country)
    reviews = []
    s = requests.Session()
    resp = s.get(initial_url, verify = False)
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
                next_url = url_template.format(next_page, product_id, country)
                resp = s.get(next_url, verify=False)

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

    return filtered_reviews


if __name__ == '__main__':
    Extract('32861942420', write_csv = True)

