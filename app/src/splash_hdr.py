import sys
import requests


class SplashHdr:

    def __init__(self, base_url, params):
        self.base_url = base_url
        self.params = params

    def get_response_text(self, url, splash_api_timeout=None):
        params = self.params
        params.update({"url": url})
        if splash_api_timeout:
            response = requests.get(self.base_url, params=params, timeout=splash_api_timeout).text
        else:
            response = requests.get(self.base_url, params=params).text
        return response

# TODO multi-container responses:
#   with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
#       futures = {
#           executor.submit(response, url, splash): url
#           for url, splash in zip(url_list, splash_list)
#       }
