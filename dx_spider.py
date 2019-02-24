import sys
import csv
import json
import requests
from pathlib import Path

from scrapy import Spider, Request
from scrapy.shell import inspect_response
from scrapy.selector import Selector


class DxSpider(Spider):
    name = 'dx_com'
    # shipping_country_codes = ['AR']
    shipping_country_codes = ['AR', 'AT', 'AU', 'BE', 'BR', 'CA', 'CH', 'CL', 'CZ', 'DE', 'DK',
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

    common_header = {'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'}
    basic_url = 'https://www.dx.com/home/product/getSpuBaseInfo'
    shipping_url = 'https://www.dx.com/home/product/getSpuShipping'
    reviews_url = 'https://www.dx.com/home/reviews/getProductReviewsLists'
    description_url = 'https://www.dx.com/home/product/getSpuDescription'
    uploaded_url = 'https://www.tntsale.com/tntsale.com/admin/tntsale.com/dx_com_scrape/Images/{}'

    def start_requests(self):
        requests = []
        if not len(sys.argv) < 4:
            urls_file = sys.argv[3].split('=')[1]
            with open(urls_file, 'r') as f:
                urls = csv.DictReader(f)
                for url in urls:
                    requests.append(Request(url=url['url'], callback=self.parse))
        return requests

    def parse(self, response):
        spu = response.css('meta[itemprop="sku"]::attr(content)').extract_first()

        yield Request(url=self.basic_url, callback=self.parse_basic_info, method='POST',
                      body='spu={}'.format(spu), headers=self.common_header, meta={
                'spu': spu,
                'url': response.url
            }, dont_filter=True)

    def parse_basic_info(self, response):
        # inspect_response(response, self)
        raw_data = json.loads(response.text)

        item = {
            'url': response.meta['url'],
            'id': raw_data['DefaultSkuCode'],
            'name': raw_data['Title'],
            'price': raw_data['HightPrice'] if raw_data['HightPrice'] else raw_data['LowPrice'],
            'category': raw_data['FirstCategoryData']['title'],
            'subcategory1': raw_data['SecondCategoryData']['title'],
            'subcategory2': '',
            'subcategory3': '',
            'shipping': [],
            'reviews': [],
            'description_text': '',
            'description_images': [],
            'image_urls': [],
            'colors': [],
            'sizes': [],
            'product_type': ''

        }

        image_urls = []
        for url_listings in raw_data['ProductImg']:
            for image_url in url_listings:
                image_urls.append('https://img.dxcdn.com{}'.format(image_url))
        item['image_urls'] = image_urls
        for attr in raw_data.get('AttrList'):
            if attr['name'] == 'Color':
                item['colors'] = [sub_attr['option_name'] for sub_attr in attr['attr']]
            if attr['name'] == 'Size':
                item['sizes'] = [sub_attr['option_name'] for sub_attr in attr['attr']]

        if item['sizes'] or item['colors']:
            item['product_type'] = 'variable'
        else:
            item['product_type'] = 'single'

        if raw_data.get('ThirdCategoryData'):
            item['subcategory2'] = raw_data.get('ThirdCategoryData', {}).get('title', '')

        if raw_data.get('FourthCategoryData'):
            item['subcategory3'] = raw_data.get('FourthCategoryData', {}).get('title', '')

        yield Request(url=self.description_url, callback=self.parse_description, method='POST',
                      body='spu={}'.format(response.meta['spu']),
                      headers=self.common_header,
                      meta={'item': item, 'spu': response.meta['spu'],
                            'review_count': raw_data['ReviewCount']}, dont_filter=True)

    def parse_description(self, response):
        item = response.meta['item']
        raw_desciption = json.loads(response.text)

        if 'Descriptions' in raw_desciption:
            raw_text = raw_desciption['Descriptions']
            selector = Selector(text=raw_text)
            desc_image_urls = selector.css('img::attr(src)').extract()
            item['description_images'] = desc_image_urls
            item['description_text'] = self.process_description(raw_text, desc_image_urls, item['id'])

        shipping_countries = self.shipping_country_codes.copy()
        current_country = shipping_countries.pop()

        yield Request(url=self.shipping_url, callback=self.parse_shipping_info, method='POST',
                      body='spu={}&count=1&country={}&skuid='.format(response.meta['spu'], current_country),
                      headers=self.common_header,
                      meta={'item': item, 'spu': response.meta['spu'], 'country_code': current_country,
                            'all_country': shipping_countries,
                            'review_count': response.meta['review_count']}, dont_filter=True)

    def parse_shipping_info(self, response):
        item = response.meta['item']
        raw_shipping_data = json.loads(response.text)
        shipping = []

        for shipping_option in raw_shipping_data:
            shipping.append({
                'id': item['id'],
                'country': response.meta['country_code'],
                'service': shipping_option['ShippingService'],
                'cost': shipping_option['Cost'],
                'estimated_time': shipping_option['EstimatedDeliveryTime'],
                'tracking_info': shipping_option['TrackingInformation']
            })

        item['shipping'] = item['shipping'] + shipping

        if response.meta['all_country']:
            current_country = response.meta['all_country'].pop()
            yield Request(url=self.shipping_url, callback=self.parse_shipping_info, method='POST',
                          body='spu={}&count=1&country={}&skuid='.format(response.meta['spu'], current_country),
                          headers=self.common_header,
                          meta={'item': item, 'country_code': current_country,
                                'all_country': response.meta['all_country'],
                                'review_count': response.meta['review_count'], 'spu': response.meta['spu']},
                          dont_filter=True)
        else:
            if not response.meta['review_count'] == 0:
                yield Request(url=self.reviews_url, callback=self.parse_reviews,
                              method='POST', body='spu={}&file_type=0&order=1&page=1'.format(response.meta['spu']),
                              headers=self.common_header,
                              meta={
                                  'item': item,
                                  'spu': response.meta['spu']
                              }, dont_filter=True)
            else:
                self.write_data(item)

    def parse_reviews(self, response):
        raw_reviews = json.loads(response.text)
        item = response.meta['item']
        reviews = []
        for review in raw_reviews['data']:
            reviews.append({
                'id': item['id'],
                'reviewer_name': review['customer_name'],
                'review_rating': review['overall_rating'],
                'review_desc': review['content'],

            })
        item['reviews'] = item['reviews'] + reviews

        if raw_reviews['current_page'] == raw_reviews['last_page']:
            self.write_data(item)
        else:
            yield Request(url=self.reviews_url, callback=self.parse_reviews,
                          method='POST', body='spu={}&file_type=0&order=1&page={}'.format(response.meta['spu'],
                                                                                          raw_reviews[
                                                                                              'current_page'] + 1),
                          headers=self.common_header,
                          meta={
                              'item': item,
                              'spu': response.meta['spu']
                          }, dont_filter=True)

    def process_description(self, desc, images, product_id):
        new_images = ['sku_{}_{}_desc.jpg'.format(product_id, index + 1) for index, image in enumerate(images)]
        for image_url, new_image_name in zip(images, new_images):
            desc = desc.replace(image_url, self.uploaded_url.format(new_image_name))

        return desc

    def download_images(self, image_urls, product_id, format_suffix='.jpg'):
        for index, image_url in enumerate(image_urls):
            with open('images/sku_{}_{}{}'.format(product_id, index + 1, format_suffix), 'wb') as f:
                f.write(requests.get(image_url).content)

    def write_data(self, item):
        reviews = item.pop('reviews')
        image_urls = item['image_urls']
        shipping = item.pop('shipping')
        description_images = item['description_images']

        if description_images:
            self.download_images(description_images, item['id'], format_suffix='_desc.jpg')
            item['description_images'] = [self.uploaded_url.format('sku_{}_{}_desc.jpg'.format(item['id'], index + 1))
                                          for index, url in enumerate(description_images)]

        if image_urls:
            self.download_images(image_urls, item['id'])
            item['image_urls'] = [self.uploaded_url.format('sku_{}_{}.jpg'.format(item['id'], index + 1))
                                  for index, image_url in enumerate(image_urls)]

        fields = list(item.keys())
        first_time = True
        if Path('basic.csv').is_file():
            first_time = False

        with open('basic.csv', 'a', encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            if first_time:
                writer.writeheader()
            writer.writerow(item)

        if shipping:
            fields = list(shipping[0].keys())
            first_time = True
            if Path('shippings.csv').is_file():
                first_time = False

            with open('shippings.csv', 'a', encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                if first_time:
                    writer.writeheader()
                writer.writerows(shipping)

        if reviews:
            fields = list(reviews[0].keys())
            first_time = True
            if Path('reviews.csv').is_file():
                first_time = False

            with open('reviews.csv', 'a', encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                if first_time:
                    writer.writeheader()
                writer.writerows(reviews)