# app.py
import os
import sys
import time

from bs4 import BeautifulSoup
from dotenv import dotenv_values
from concurrent.futures import ThreadPoolExecutor, as_completed

# Custom imports
import general_methods as gm
import web_general_methods as wgm
import files_general_methods as fgm

from searx_hdr import SearXhdr
from splash_hdr import SplashHdr


# # ===== Global Variables ===================================================================== Global Variables =====
...
# # ===== Global Variables ===================================================================== Global Variables =====
...
# Load config data
dot_env_filename = ".env"
if os.path.exists(f"{dot_env_filename}"):
    config = dotenv_values(f"{dot_env_filename}")
elif os.path.exists(f"./src/{dot_env_filename}"):
    config = dotenv_values(f"./src/{dot_env_filename}")
elif os.path.exists(f"./app/src/{dot_env_filename}"):
    config = dotenv_values(f"./app/src/{dot_env_filename}")
else:
    raise ImportError

# PrintMode instance
pm = gm.PrintMode(
    [x for x in ['DEBUG', 'WARNING', 'ERROR', 'INFO'] if config[x] == "YES"],
    timestamp_key=(config['TIMESTAMP_KEY'] == "TRUE")
)

# DirectoriesHandler
dh = fgm.DirectoriesHandler()
BASE_DIR = dh.base_dir
DB_DATA_DIR = dh.db_data
dh.dirs.update(
    {
        "db_data": dh.db_data,
    }
)
dh.dirs_to_remove.update(
    {
        "db_data": dh.dirs["db_data"]
    }
)

# SearX config
SEARX_BASE_URL = config['SEARX_BASE_URL']
searx = SearXhdr(searx_base_url=SEARX_BASE_URL)


# Splash config
SPLASH_BASE_URL = config['SPLASH_BASE_URL']
SPLASH_PARAMS = {
    "wait": config['SPLASH_PARAMS_WAIT'],
    "timeout": config['SPLASH_PARAMS_TIMEOUT'],
    "resource_timeout": config['REQUEST_TIMEOUT'],
    "images": config['IMAGES'],
}
SPLASH_INSTANCES = fgm.json_read(f"{dh.temp}splash_containers_data.json")
splash_list = [
    SplashHdr(f"http://{splash_instance['ip']}:8050/render.html", SPLASH_PARAMS)
    for splash_instance in SPLASH_INSTANCES
]

# Threads
MAX_WORKERS = int(config["INSTANCES_NUMBER"])


# # ===== App logic =================================================================================== App logic =====
...
# # ===== App logic =================================================================================== App logic =====


def select_one_of_list(soup, css_selector_list):
    for css_selector in css_selector_list:
        try:
            selected_item = soup.select_one(css_selector)
            if selected_item is not None:
                return selected_item
        except:
            continue


def drop_blacklist_domains(url_list):
    # NOT inurl:(alibaba OR aliexpress OR amazon OR ebay)
    blocklist_domains = [
        "https://www.esources.co.uk",
        "https://esources.co.uk",
        "https://www.globalsources.com",
        "https://globalsources.com",
        "https://www.go4worldbusiness.com",
        "https://go4worldbusiness.com",
        "https://b2b.hurtel.com",
        "https://mpdmobileparts.com",
        "https://www.lusha.com",
        "https://lusha.com",
        "https://www.glassdoor.com",
        "https://glassdoor.com",
        "https://www.tvh.com",
        "https://tvh.com",
        "https://www.yelp.com",
        "https://yelp.com",
        "https://www.ankorstore.com",
        "https://ankorstore.com",

        "ebay.com",
        "ebay.co",
        "alibaba.com",
        "aliexpress.com",
        "amazon.com",
        "amazon.co",
        ".apple.com",
        "/apple.com",
        "microsoft.com",
        "quora.com",
        "europages.co.uk",
        "china.cn",
        "made-in-china.com",
        "linkedin.com",
        "facebook.com",
        "twitter.com",
        "tradeholding.com",
        ".etsy.com",
        "/etsy.com",
        "/wikipedia.org",
        ".wikipedia.org",
    ]
    result_url_list = []
    for url in url_list:
        base_url = gm.url_to_base_url(url)
        check_list = [x for x in blocklist_domains if x in base_url]
        if len(check_list) > 0:
            continue
        else:
            result_url_list.append(url)

    return result_url_list


def get_search_url_list(from_file=False):

    if from_file:
        result_files = dh.get_file_names(DB_DATA_DIR)
        try:
            last_file_path = f"{DB_DATA_DIR}{max([x for x in result_files if 'clean_url_list.json' in x])}"
            url_list = fgm.json_read(last_file_path)

        # If file doesn't exist
        except Exception as _ex:
            pm.error(f"Couldn't read from a file")
            return get_search_url_list()

    else:
        countries = [
            "Austria",
            "Belgium",
            "Bulgaria",
            "Switzerland",
            "Cyprus",
            "Czech Republic",
            "Germany",
            "Denmark",
            "Estonia",
            "Greece",
            "Spain",
            "Finland",
            "France",
            "Croatia",
            "Hungary",
            "Ireland",
            "Iceland",
            "Italy",
            "Liechtenstein",
            "Lithuania",
            "Luxembourg",
            "Latvia",
            "Malta",
            "Netherlands",
            "Norway",
            "Poland",
            "Portugal",
            "Romania",
            "Sweden",
            "Slovenia",
            "Slovakia",
            "United Kingdom",
        ]
        clean_url_list = []
        url_list = []
        results_json = []

        for country in countries:
            response_data = searx.search_many_pages(
                f'"{country}" phone parts company intitle:"wholesale" -dnb.com',
                end_page=3,
                search_settings="!go"
            )

            results_json.append(response_data.json())
            url_list.extend(response_data.get_urls())
            clean_url_list.extend(drop_blacklist_domains(response_data.get_urls()))

        fgm.json_rewrite(f"{DB_DATA_DIR}results_json.json", results_json)
        fgm.json_rewrite(f"{DB_DATA_DIR}url_list.json", url_list)
        fgm.json_rewrite(f"{DB_DATA_DIR}clean_url_list.json", clean_url_list)

    return url_list


def find_contacts_page(url, splash: SplashHdr):
    base_url = gm.url_to_base_url(url)
    pm.info(f"Find contacts for: {url}")
    response_text = splash.get_response_text(url)
    page_soup = BeautifulSoup(response_text, "lxml")
    fgm.text_rewrite(f"{DB_DATA_DIR}{base_url.replace('/','_').replace(':', '')}_main_page.html", str(page_soup))

    key_word_list = [
        "Contact Us",
        "Connect with us",
        "Contact with",
        "Contact",
        "Get In Touch With Us",
        "Get In Touch With",
        "Get In Touch",
        "About Us",
        "About",
    ]

    contacts_tag = None
    for x in page_soup.select("a"):
        for key_word in key_word_list:
            if key_word.lower() in x.text.lower():
                contacts_tag = x
                break

        if contacts_tag is not None:
            break

    if contacts_tag is not None:
        pm.debug(f"contacts_tag: {contacts_tag}")
        return {base_url: gm.repair_url(contacts_tag['href'], base_url)}
    else:
        pm.warning(f"contacts_tag is None: {base_url}")
        return {base_url: None}


def get_contacts_dict(url_list, from_file=False):

    # If from_file == True
    if from_file:
        result_files = dh.get_file_names(DB_DATA_DIR)
        try:
            last_file_path = f"{DB_DATA_DIR}{max([x for x in result_files if 'contacts_dict.json' in x])}"
            return fgm.json_read(last_file_path)

        # If file doesn't exist
        except Exception as _ex:
            pm.error(f"Couldn't read from a file")
            return get_contacts_dict(url_list)

    # If from_file == False
    contacts_dict = {}
    url_iterator = gm.UrlIterator(url_list, MAX_WORKERS)
    for url_list in url_iterator:

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {
                executor.submit(find_contacts_page, url, splash): url
                for url, splash in zip(url_list, splash_list)
            }

            # Process the results
            for future in as_completed(futures):
                url = futures[future]

                # Try to get data concurrently
                try:
                    res = future.result()
                    if res is not None:
                        contacts_dict.update(res)

                # If there is any issue try to get data sequentially
                except Exception as _ex:
                    pm.error(f"Error while executing '{url}': {_ex}")
                    contacts_dict.update({gm.url_to_base_url(url): None})
                    pm.error(f"Couldn't get a contacts url for: {url}")
                    time.sleep(10)

    fgm.json_rewrite(f"{DB_DATA_DIR}contacts_dict.json", contacts_dict)
    return contacts_dict


def find_contacts_data(contacts_url):
    url = [*contacts_url.values()][0]
    base_url = [*contacts_url.keys()][0]
    pm.info(f"Find contacts data for: {url}")
    response_text = splash.get_response_text(url)
    page_soup = BeautifulSoup(response_text, "lxml")
    fgm.text_rewrite(f"{DB_DATA_DIR}{base_url.replace('/', '_').replace(':', '')}_contacts.html", str(page_soup))

    css_selector_list = [
        'div[class*="contact"]',
        'div[class*="contact"]',
    ]

    contacts_tag = None
    for x in page_soup.select("a"):
        for key_word in key_word_list:
            if key_word.lower() in x.text.lower():
                contacts_tag = x
                break

        if contacts_tag is not None:
            break

    if contacts_tag is not None:
        pm.debug(f"contacts_tag: {contacts_tag}")
        return {base_url: gm.repair_url(contacts_tag['href'], base_url)}
    else:
        pm.warning(f"contacts_tag is None: {base_url}")
        return {base_url: None}


def get_contacts_data(contacts_dict):
    # Create list [{base_url: url}, {} ...]
    contacts_url_list = [{
        base_url: url
        for base_url, url in zip(contacts_dict.keys(), contacts_dict.values())
        if url is not None
    }]

    # Result json [{"base_url": url, "contacts_url": url, "contacts_data": data_str}, {} ...]
    contacts_data_json = []
    contacts_url_iterator = gm.UrlIterator(contacts_url_list, MAX_WORKERS)
    for contacts_url_list in contacts_url_iterator:

        # Concurrent retries == 2
        for _concurrent_try_counter in range(2):
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                futures = {
                    executor.submit(find_contacts_data, contacts_url): contacts_url
                    for contacts_url in contacts_url_list
                }

                # Process the results
                for future in as_completed(futures):
                    contacts_url = futures[future]

                    # Try to get data concurrently
                    try:
                        res = future.result()
                        if res is not None:
                            contacts_data_json.append(res)

                    # If there is any issue, try to get data sequentially
                    except Exception as _ex:
                        pm.error(f"Error while executing '{contacts_url}': {_ex}")
                        time.sleep(20)
                        executor.shutdown()

                        for contacts_url in contacts_url_list:

                            # Sequentially retries == 3
                            for _sequentially_try_counter in range(3):
                                try:
                                    contacts_data_json.append(find_contacts_data(contacts_url))
                                    break
                                except Exception as _ex:
                                    # Sleep and retry
                                    pm.warning(f"Something went wrong: '{contacts_url}': {_ex}")
                                    time.sleep(20)

                                # If all the reties are failed, add None as result to the result dict
                                failed_result = {
                                    "base_url": [*contacts_url.keys()][0],
                                    "contacts_url": [*contacts_url.values()][0],
                                    "contacts_data": None
                                }
                                contacts_data_json.append({contacts_url})
                                pm.error(f"Couldn't get a contacts url for: {contacts_url}")
                        break
            break

    fgm.json_rewrite(f"{DB_DATA_DIR}contacts_data.json", contacts_dict)
    return contacts_dict


# # ===== Start app =================================================================================== Start app =====
...
# # ===== Start app =================================================================================== Start app =====


def start_app():
    # dh.recreate_dirs()
    fgm.remove_files_by_extension(dh.db_data, "html")

    # TODO: update key // update url_list
    url_list = get_search_url_list(from_file=True)

    # Get list of Contacts/About Us urls
    # TODO: first, check if there is "/contact" or "/about_us" etc
    contacts_dict = get_contacts_dict(url_list, from_file=False)

    sys.exit()
    # Get contacts data to future sorting
    contacts_data_list = get_contacts_data(contacts_dict)


def anchor():
    pass


if __name__ == '__main__':
    start_app()
