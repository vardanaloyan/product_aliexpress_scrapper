import pickle
from selenium import webdriver

browser = webdriver.Firefox()


def get_cookies():
    browser.get("https://login.aliexpress.com/buyer.htm?return=https%3A%2F%2Fwww.aliexpress.com%2F&random=CEA73DF4D81D4775227F78080B9B6126")
    print('input your username and password in Firefox and hit Submit')
    input('Hit Enter here if you have summited the form: <Enter>')
    cookies = browser.get_cookies()
    pickle.dump(cookies, open("cookies.pickle", "wb"))


def set_cookies():
    browser.get("https://aliexpress.com")
    cookies = pickle.load(open("cookies.pickle", "rb"))
    for cookie in cookies:
        browser.add_cookie(cookie)
    browser.get("https://bestselling.aliexpress.com/en")


if __name__ == '__main__':
    get_cookies()

