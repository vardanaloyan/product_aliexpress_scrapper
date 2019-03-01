#!/usr/bin/env python3
import csv
import requests
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

# shipping_country_codes =     ['AR', 'AT', 'AU', 'BE']

def extract_product_shipping(product_id, country, unit = "USD"):
    shippings_tmp = []
    url_template = 'https://freight.aliexpress.com/ajaxFreightCalculateService.htm?callback=jQuery1830650128321702308_1551079034704&f=d&productid={product_id}&count=1&minPrice=5.30&maxPrice=5.30&currencyCode={currencyCode}&transactionCurrencyCode={transactionCurrencyCode}&sendGoodsCountry=&country={country}&province=&city=&abVersion=1&_=1551080238699'
    currencyCode = transactionCurrencyCode = unit
    initial_url = url_template.format(product_id = product_id, currencyCode = currencyCode, transactionCurrencyCode=transactionCurrencyCode, country = country)

    s = requests.Session()

    resp = s.get(initial_url, verify=False)
    if resp.status_code == 200:
        data = str(resp.content)
        #print (country, data, len(data))
        if len(data) != 3:
            data = data.split('(')[1].strip("'").strip(')')
            # print (data)
            # print ('\n'*10)
            false = "false"
            true = "true"
            null = "null"
            data = eval(data)
            data = data["freight"]
            for dct in data:
#            print 'country: ', country, ', company: ', dct['companyDisplayName'], ', EstimatedTime: ', dct['time'], ', cost: ', dct['price'], ', tracked: ',dct['isTracked']
                temp_dct = dict(productid = product_id, country = country, company = dct['companyDisplayName'],  cost = dct['price']+ ' %s' %currencyCode, estimatedTime = dct['time'] + ' days', tracked = dct['isTracked'])
                shippings_tmp.append(temp_dct)
        else:
            return None
    return shippings_tmp

def iterShipping(product_id, write_csv = False):
    shippings = []
    for i, country in enumerate(shipping_country_codes):
        #if i <= 190: continue
        _tmp = extract_product_shipping(product_id, country)
        if _tmp is not None:
            shippings += _tmp
        print ("SHIPPING: {}\t{}/{} ".format(product_id, i+1, len(shipping_country_codes)))
    
    keys = ['productid', 'country', 'company', 'cost', 'estimatedTime', 'tracked']

    itr = 0
    if write_csv:
        with open('shippings_%s.csv' % product_id, 'w') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            if itr == 0:
                dict_writer.writeheader()
                itr += 1
            dict_writer.writerows(shippings)
    return keys, shippings

if __name__ == '__main__':
    iterShipping('32861942420',  write_csv = True)


