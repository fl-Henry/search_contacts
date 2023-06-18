import sys
import requests


class SplashHdr:

    def __init__(self, base_url, params):
        self.base_url = base_url
        self.params = params

    def get_response_text(self, url):
        params = self.params
        params.update({"url": url})
        response = requests.get(self.base_url, params=params).text
        return response
