# web_general_methods.py
import sys
import json
import random
import requests

from fake_headers import Headers
from bs4 import BeautifulSoup


def get_headers():
    __os = ('win', 'mac', 'lin')
    __browser = ('chrome', 'firefox', 'opera')
    random_browser = __browser[random.randint(0, len(__browser) - 1)]
    random_os = __os[random.randint(0, len(__os) - 1)]
    return Headers(os=random_os, browser=random_browser, headers=True).generate()


def get_response_text(url):
    return requests.get(url, headers=get_headers()).text


def get_soup(text):
    return BeautifulSoup(text, "lxml")
