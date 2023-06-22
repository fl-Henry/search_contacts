# web_general_methods.py
import sys
import json
import random
import requests

from urllib.request import urlopen
from fake_headers import Headers
from bs4 import BeautifulSoup
from lxml import etree


def get_headers():
    __os = ('win', 'mac', 'lin')
    __browser = ('chrome', 'firefox', 'opera')
    random_browser = __browser[random.randint(0, len(__browser) - 1)]
    random_os = __os[random.randint(0, len(__os) - 1)]
    return Headers(os=random_os, browser=random_browser, headers=True).generate()


def get_response_text(url):
    return requests.get(url, headers=get_headers()).text


def get_soup(text):
    return BeautifulSoup(str(text), "lxml")


def find_xpath(soup, xpath_selector):
    dom = etree.HTML(str(soup))
    selected_items = dom.xpath(xpath_selector)
    if len(selected_items) > 0:
        return [get_soup(etree.tostring(x)) for x in selected_items]
    else:
        return []


def find_one_xpath(soup, xpath_selector):
    selected_items_soup = find_xpath(soup, xpath_selector)
    if len(selected_items_soup) > 0:
        return selected_items_soup[0]
    else:
        return []
