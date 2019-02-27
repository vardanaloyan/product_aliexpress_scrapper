import basic
import review
import shipping
import csv

def readUrls(file):
	urls_list = []
	with open(file, 'r') as f:
		urls = csv.DictReader(f)
		for url in urls:
			urls_list.append(url['url'])
	return urls_list


if __name__ == "__main__":
	urls = readUrls('urls.csv')
	header = True
	f_basic = open('BASIC.csv', 'w', encoding="utf-8")
	f_review = open('REVIEW.csv', 'w', encoding="utf-8")
	f_shipping = open('SHIPPING.csv', 'w', encoding="utf-8")

	for url in urls:
		basic_field, basic_dct = basic.extract_product_info(url)
		review_field, review_dct = review.extract_product_reviews(basic_dct['product_id'])
		shipping_field, shipping_dct = shipping.iterShipping(basic_dct['product_id'])
		writer_basic = csv.DictWriter(f_basic, basic_field)
		writer_review = csv.DictWriter(f_review, review_field)
		writer_shipping = csv.DictWriter(f_shipping, shipping_field)
		if header:
			header = False
			writer_basic.writeheader()
			writer_review.writeheader()
			writer_shipping.writeheader()
		writer_basic.writerow(basic_dct)
		writer_review.writerows(review_dct)
		writer_shipping.writerows(shipping_dct)