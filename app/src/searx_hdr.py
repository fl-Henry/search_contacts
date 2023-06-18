# searx_hdr.py
import json
import requests

# Custom imports
import general_methods as gm


class Response(object):

    def __init__(self, raw_response):
        self.raw_response = raw_response
        self.pm = gm.PrintMode()

    def __str__(self):
        return self.raw_response.text

    def __repr__(self):
        return self.__str__()

    def __call__(self, *args, **kwargs):
        return self.json()

    def json(self):
        return json.loads(self.raw_response.text)

    def get_results(self):
        """
            Returns json of results if response is not None
        :return:
        """
        return json.loads(self.raw_response.text)["results"]

    def get_urls(self):
        """
            returns list of urls if response is not None
        :return:
        """
        return [x["url"] for x in json.loads(self.raw_response.text)["results"]]


class ManyResponses:

    def __init__(self, raw_response_list: list[Response]):
        self.raw_response_list = raw_response_list
        self.pm = gm.PrintMode()

    def __str__(self):
        return str([str(x) for x in self.raw_response_list])

    def __repr__(self):
        return self.__str__()

    def __call__(self, *args, **kwargs):
        return self.json()

    def json(self):
        return [x.json() for x in self.raw_response_list]

    def get_results(self):
        """
            Returns json of results if response is not None
        :return:
        """
        return [x.get_results() for x in self.raw_response_list]

    def get_urls(self):
        """
            returns list of urls if response is not None
        :return:
        """
        url_list = []
        [url_list.extend(x.get_urls()) for x in self.raw_response_list]
        return url_list


class SearXhdr:

    def __init__(
            self,
            searx_base_url: str = 'http://localhost:8080/search',
            last_response: Response | None = None,
            print_key: bool = True,
            print_err_key: bool = True,
            search_settings: str = "!go",
            formats: str = 'json'
    ):
        self.base_url = searx_base_url
        self.last_response = last_response
        self.print_key = print_key
        self.print_err_key = print_err_key
        self.search_settings = search_settings
        self.formats = formats
        self.pm = gm.PrintMode()

    @staticmethod
    def _default_if_none(value, default_value):
        if value is None:
            return default_value
        else:
            return value

    def search(self, search_query, page: int = 1, formats: str = None, search_settings: str = None):
        """
            Search syntax: https://docs.searxng.org/user/search-syntax.html#search-syntax
        :param search_query: str        | 'cute kitten'
        :param formats: str             | [html, csv, json, rss]
        :param page: int                | search page
        :param search_settings: str     | To set category and/or engine names use a ! prefix.
        :return:
        """

        formats = self._default_if_none(formats, self.formats)
        search_settings = self._default_if_none(search_settings, self.search_settings)

        data = {
            'q': f'{search_settings} {search_query}',
            'format': formats,
            "pageno": page,
        }
        self.pm.info(f'Format: {data["format"]}; Page: {data.get("pageno")} Search query: {repr(data["q"])}')
        response = requests.get(self.base_url, params=data)

        # Return class Response
        return Response(response)

    def search_many_pages(
            self, search_query, start_page=1, end_page=None,
            formats: str = None, search_settings: str = None
    ):
        """
            Returns all responses for pages between start_page and end_page
            Search syntax: https://docs.searxng.org/user/search-syntax.html#search-syntax
        :param search_query: str        | 'cute kitten'
        :param start_page: int          | 1
        :param end_page: int            | 10
        :param formats: str             | [html, csv, json, rss]
        :param search_settings: str     | To set category and/or engine names use a ! prefix.
        :return:
        """
        # Check if end_page is None
        if end_page is None:
            self.pm.error("end_page is None. Specify end_page value or use 'search()' instead")
            raise ValueError

        # Get all page responses and append to response_list
        response_list = []
        for page in range(start_page, end_page + 1):
            response = self.search(
                search_query=search_query,
                formats=formats,
                page=page,
                search_settings=search_settings,
            )
            response_list.append(response)

        return ManyResponses(response_list)


def main():
    pass


if __name__ == '__main__':
    main()

