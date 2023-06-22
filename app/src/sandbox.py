from duckduckgo_search import DDGS

with DDGS() as ddgs:
    search_query = "France wholesale phone spare parts"
    for r in ddgs.text(search_query, safesearch='Off'):
        print(r['href'])
