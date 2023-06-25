# app.py
import os
import sys
import time
import json
import datetime

from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
from dotenv import dotenv_values
from concurrent.futures import ThreadPoolExecutor, as_completed

# Custom imports
import general_methods as gm
import web_general_methods as wgm
import files_general_methods as fgm

from openai_api import ChatGPT
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
ATTEMPT_DIR = DB_DATA_DIR
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
    SplashHdr(f"http://{splash_instance['ip']}/render.html", SPLASH_PARAMS)
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


def clear_url_list(url_list):
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
        "https://www.carousell.ph",
        "https://www.kodak.com",
        "https://www.ikea",

        "info",
        "search",
        "auto",
        "avto",
        "motors",
        "motor/",
        "motor.",
        "motorcycle",
        "vehicle",
        "market",
        "markt",
        "marketplace",
        "news",
        "library",
        "blog",
        "document",
        "docs/",
        "/docs",
        "/view",
        "view/",
        "statistics",
        "providers",
        "google",
        "suppliers",
        "india",
        "manufacturers",
        "distributors",
        "firm",
        "cars/",
        "cars.",
        "car.",
        "car/",
        "truck",
        "engine",
        "agra",
        "/mall",
        "mall/",
        ".mall",
        "mall.",

        "dhgate.com",
        "yellow.place",
        ".edu",
        ".wiki",
        "pinterest.com",
        "ebay.com",
        "ebay.co",
        "ebay.",
        "alibaba.com",
        "aliexpress.com",
        "instagram.com",
        "amazon.com",
        "amazon.co",
        ".apple.com",
        "/apple.com",
        "microsoft.com",
        "quora.com",
        "europages.co.uk",
        "europages",
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
        "merkandi.",
    ]
    result_url_list = []
    for url in url_list:
        if url[-4:] not in [".doc", '.pdf']:
            # base_url = gm.url_to_base_url(url)
            check_list = [x for x in blocklist_domains if x.lower() in url.lower()]
            if len(check_list) > 0:
                continue
            else:
                result_url_list.append(url)

    base_url_list = []
    clean_url_list = []
    for url in result_url_list:
        if gm.url_to_base_url(url) not in base_url_list:
            base_url_list.append(gm.url_to_base_url(url))
            clean_url_list.append(url)

    return clean_url_list


def get_search_url_list(from_file=False):

    if from_file:
        result_files = dh.get_file_names(ATTEMPT_DIR)
        try:
            last_file_path = f"{ATTEMPT_DIR}{max([x for x in result_files if 'clean_inst_url_list.json' in x])}"
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

        countries = [
            "Österreich Handy Ersatzteile Großhandel",
            "Groothandel in reserveonderdelen voor mobiele telefoons in België",
            "България мобилни iphone резервни части на едро",
            "Schweiz Handy Ersatzteile Großhandel",
            "Ανταλλακτικά κινητών iphone Κύπρου χονδρική",
            "Česká republika velkoobchod náhradních dílů na mobilní iphone",
            "Deutschland Handy-iPhone-Ersatzteile im Großhandel",
            "Danmark mobil iphone reservedele engros",
            "Eesti mobiiltelefonide iphone varuosade hulgimüük",
            "Ελλάδα ανταλλακτικά κινητών iphone χονδρική",
            "España recambios móviles iphone al por mayor",
            "Suomi matkapuhelin iphone varaosien tukkumyynti",
            "Vente en gros de pièces détachées iphone mobile France",
            "Hrvatska veleprodaja rezervnih dijelova za mobitele iphone",
            "Magyarország mobil iphone alkatrész nagykereskedés",
            "mórdhíola páirteanna spártha iphone soghluaiste na hÉireann",
            "Iceland farsíma iphone varahlutir heildsölu",
            "Commercio all'ingrosso di pezzi di ricambio per iPhone mobili in Italia",
            "Liechtensteiner Handy-iPhone-Ersatzteile im Großhandel",
            "Lietuva mobiliųjų iphone atsarginių dalių didmeninė prekyba",
            "Lëtzebuerger Handy iphone Ersatzdeeler Grousshandel",
            "Latvija mobilo iphone rezerves daļu vairumtirdzniecība",
            "Malta mobile iphone spare parts bl-ingrossa",
            "Groothandel in mobiele iPhone onderdelen in Nederland",
            "Norge mobil iphone reservedeler engros",
            "Sprzedaż hurtowa części zamiennych do iPhone'ów w Polsce",
            "Venda por grosso de peças sobressalentes para iphone móvel em portugal",
            "Romania mobil iphone piese de schimb en-gros",
            "Sverige mobil iphone reservdelar grossist",
            "Slovenija mobilni iphone rezervni deli veleprodaja",
            "Slovensko veľkoobchod s náhradnými dielmi pre mobilné telefóny iphone",
            "United Kingdom mobile iphone spare parts wholesale",
        ]
        clean_url_list = []
        url_list = []
        results_json = []

        for country in countries:
            # response_data = searx.search_many_pages(
            #     f'intitle:{country} intitle:"wholesale" intext:"mobile phone spare parts suppliers" OR intext:"mobile phone spare parts distributors" OR intext:"mobile phone spare parts wholesalers" OR intext:"mobile phone spare parts manufacturers" -china',
            #     end_page=3,
            #     search_settings="!go"
            # )
            time.sleep(2)
            try:
                with DDGS() as ddgs:
                    # search_query = f'{country} mobile iphone spare parts wholesale'
                    search_query = f'{country}'
                    pm.debug(search_query)
                    for r in ddgs.text(search_query, safesearch='Off'):
                        url_list.append(r['href'])

            except:
                pm.error("Couldn't get results for:", search_query)
            # results_json.append(response_data.json())

            # url_list.extend(response_data.get_urls())

        # fgm.json_rewrite(f"{ATTEMPT_DIR}results_json.json", results_json)
        fgm.json_rewrite(f"{ATTEMPT_DIR}url_list.json", url_list)

        url_list = clear_url_list(url_list)
        fgm.json_rewrite(f"{ATTEMPT_DIR}clean_inst_url_list.json", url_list)
    return url_list


def find_contacts_page(url, splash: SplashHdr):
    base_url = gm.url_to_base_url(url)
    pm.info(f"Find contacts for: {url}")
    response_text = splash.get_response_text(url)
    page_soup = BeautifulSoup(str(response_text).lower(), "lxml")
    # fgm.text_rewrite(f"{ATTEMPT_DIR}{base_url.replace('/','_').replace(':', '')}_main_page.html", str(page_soup))

    key_word_list = [
        "contact us",
        "connect with us",
        "contact with",
        "contact",
        "get in touch with ws",
        "get in touch with",
        "get in touch",
        "about us",
        "about",

        "Kontaktiraj nas",
        "poveži se sa nama",
        "kontaktirati sa",
        "kontakt",
        "kontaktirajte sa ws",
        "stupiti u kontakt sa",
        "javi se",
        "o nama",
        # "oko",

        "свържете се с нас",
        "Свържи се с нас",
        "Свържи се с",
        "контакт",
        "свържете се с ws",
        "се свържете с",
        "свържете се",
        "за нас",
        "относно",

        "contacta amb nosaltres",
        "connecta amb nosaltres",
        "contacta amb",
        "contacte",
        "posa't en contacte amb ws",
        "estar en contacte amb",
        "posar-se en contacte",
        "sobre nosaltres",
        # "Sobre",

        "cuntatta ci",
        "cunnetta cun noi",
        "cuntattu cù",
        "cuntattu",
        "contattate cù ws",
        "contattate cù",
        "contattate",
        "nantu à noi",
        # "circa",

        "Kontaktirajte nas",
        "Poveži se s nama",
        "stupiti u kontakt sa",
        "kontakt",
        "stupati u kontakt s ws",
        "doći u dodir s",
        "javite se",
        "o nama",
        # "oko",

        "kontaktujte nás",
        "spojit se s námi",
        "kontakt s",
        "Kontakt",
        "kontaktujte ws",
        "dostat se do kontaktu s",
        "být v kontaktu",
        "o nás",
        # "o",

        "kontakt os",
        "kontakt os",
        "kontakt med",
        "kontakt",
        "kom i kontakt med ws",
        "komme i kontakt med",
        "ta kontakt",
        "om os",
        # "om",

        "Neem contact met ons op",
        "Verbind je met ons",
        "contact met",
        "contact",
        "neem contact op met ws",
        "in contact komen met",
        "neem contact op",
        "over ons",
        # "over",

        "võta meiega ühendust",
        "võta meiega ühendust",
        "kontakt"
        "kontakt",
        "võta ühendust ws-iga",
        "ühendusse astuma",
        "ühendust võtma",
        "meist",
        "umbes",

        "ota meihin yhteyttä",
        "ota meihin yhteyttä",
        "ottaa yhteyttä",
        "ottaa yhteyttä",
        "ota yhteyttä ws:ään",
        "ottaa yhteyttä",
        "ota yhteyttä",
        "meistä",
        # "noin",

        "Contactez-nous",
        "Connecte-toi avec nous",
        "entrer en contact avec",
        "contact",
        "entrer en contact avec ws",
        "entrer en contact avec",
        "entrer en contact",
        "à propos de nous",
        "à propos de",

        "kontaktiere uns",
        "verbinde dich mit uns",
        "Kontakt mit",
        "Kontakt",
        "Nehmen Sie Kontakt mit ws auf",
        "Kontakt aufnehmen mit",
        "in Kontakt kommen",
        "über uns",
        # "um",

        "επικοινωνήστε μαζί μας",
        "συνδεθείτε μαζί μας",
        "επικοινωνήστε με",
        "Επικοινωνία",
        "Επικοινωνήστε με το ws",
        "να έρθετε σε επαφή με",
        "έρχομαι σε επαφή",
        "σχετικά με εμάς",
        "σχετικά με",

        "lépjen kapcsolatba velünk",
        "csatlakozz hozzánk",
        "kapcsolatba lépni",
        "kapcsolatba lépni",
        "vegye fel a kapcsolatot ws-vel",
        "vegye fel a kapcsolatot",
        "felveszi a kapcsolatot",
        "rólunk",
        "ról ről",

        "Hafðu samband við okkur",
        "tengdu okkur",
        "samband við",
        "hafðu samband",
        "hafðu samband við ws",
        "komast í samband við",
        "komast í samband",
        "um okkur",
        # "um",

        "Glaoigh orainn",
        "ceangal linn",
        "Teagmháil le",
        "teagmháil",
        "téigh i dteagmháil le ws",
        "téigh i dteagmháil le",
        "Téigh i dteagmháil",
        "Fúinn",
        # "faoi",

        "Contattaci",
        "Connettiti con noi",
        "contatto con",
        "contatto",
        "mettiti in contatto con ws",
        "entrare in contatto con",
        "contattaci",
        "chi siamo",
        # "Di",

        "Sazinies ar mums",
        "Sazinieties ar mums",
        "kontaktēties ar",
        "kontakts",
        "sazinieties ar ws",
        "Sazināties ar",
        "Sazināties",
        "par mums",
        # "par",

        "Susisiekite su mumis",
        "Susiekite su mumis"
        "Susisiekti su",
        "kontaktas",
        "susisiekti su ws",
        "Susisiekite su",
        "susisiekti",
        "apie mus",
        # "apie",

        "kontaktéiert eis",
        "verbindt mat eis",
        "Kontakt mat",
        "kontakt",
        "kontaktéiert ws",
        "kontaktéiert mat",
        "Kontaktéieren",
        "iwwer eis",
        "iwwer",

        "Контактирајте не",
        "поврзете се со нас",
        "поврзи се со нас"
        "Контактирај со",
        "контакт",
        "стапи во контакт со ws",
        "да стапат во контакт со",
        "стапи во контакт",
        "за нас",
        # "за",

        "kontakt oss",
        "kontakt oss",
        "kontakt med",
        "kontakt",
        "ta kontakt med ws",
        "komme i kontakt med",
        "Ta kontakt",
        "om oss",
        # "Om",

        "Skontaktuj się z nami",
        "Połącz się z nami",
        "kontakt z",
        "kontakt",
        "skontaktuj się z ws",
        "skontaktować się z",
        "skontaktować się",
        "o nas",
        # "o",

        "Contate-nos",
        "conecte-se conosco",
        "contato com",
        "contato",
        "entre em contato com ws",
        "entre em contato com",
        "entrar em contato",
        "sobre nós",
        "sobre",

        "contactaţi-ne",
        "conecteaza-te cu noi",
        "contactul cu",
        "a lua legatura",
        "luați legătura cu ws",
        "intra in contact cu",
        "Intrați în legătură",
        "despre noi",
        "despre",

        "kontaktuj nás",
        "Spojte sa s nami",
        "kontakt s",
        "kontakt",
        "kontaktujte ws",
        "dostať sa do kontaktu s",
        "kontaktovať",
        "o nás",
        # "o",

        "kontaktiraj nas",
        "povežite se z nami",
        "stik z",
        # "stik",
        "stopiti v stik z ws",
        "priti v stik z",
        "stopite v stik",
        "o nas",
        "približno",

        "Contáctenos",
        "Conéctate con nosotros",
        "contactar con",
        "contacto",
        "ponerse en contacto con ws",
        "estar en contacto con",
        "Ponerse en contacto",
        "sobre nosotros",
        "acerca de",

        "kontakta oss",
        "kontakta oss",
        "kontakt med",
        "Kontakt",
        "komma i kontakt med ws",
        "hålla kontakten med",
        "komma i kontakt",
        "om oss",
        "handla om",


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
        try:
            last_file_path = f"{ATTEMPT_DIR}contacts_dict.json"
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
                    time.sleep(10)

    fgm.json_rewrite(f"{ATTEMPT_DIR}contacts_dict.json", contacts_dict)
    return contacts_dict


def find_by_xpath_list(xpath_list, soup, max_find_counter=2):
    find_counter = 1
    found_items_list = []
    for xpath in xpath_list:
        try:
            tags = wgm.find_xpath(soup, xpath)
            if len(tags) > 0:
                find_counter += 1
                found_items_list.append([str(x) for x in tags])

                if find_counter > max_find_counter:
                    break
        except:
            continue

    return found_items_list


def find_contacts_data(contacts_url, splash):
    url = [*contacts_url.values()][0]
    base_url = [*contacts_url.keys()][0]
    pm.info(f"Find contacts data for: {url}")
    response_text = splash.get_response_text(url)
    page_soup = BeautifulSoup(str(response_text).lower(), "lxml")
    # fgm.text_rewrite(f"{ATTEMPT_DIR}{base_url.replace('/', '_').replace(':', '')}_contacts.html", str(page_soup))

    xpath_address_list = [
        '//*[contains(text(), "address")]/ancestor::div[1]',
        '//*[contains(@class, "address")]/ancestor::ul[1]',
        '//*[contains(@class, "address")]/ancestor::ul[1]',
        '//*[contains(text(), "address")]/ancestor::ul[1]',
    ]

    xpath_phone_list = [

        "//*[text()='telephone']/ancestor::div[1]",
        "//*[@class='telephone']/ancestor::div[1]",
        "//*[@class='phone']/ancestor::div[1]",
        "//*[text()='phone:']/ancestor::div[1]",
        "//*[text()='phone:']/ancestor::ul[1]",
    ]

    xpath_mail_list = [
        '//*[contains(text(), "@")]/ancestor::div[1]',
        '//*[contains(text(), "email")]/ancestor::div[1]',
        '//*[contains(text(), "e-mail")]/ancestor::div[1]',
        '//*[contains(@href, "mailto")]/ancestor::div[1]',
        '//*[contains(text(), "email")]/ancestor::div[contains(@class, "footer")][1]',

        '//*[contains(text(), "email")]/ancestor::ul[1]',
        '//*[contains(text(), "e-mail")]/ancestor::ul[1]',
        '//*[contains(text(), "E-mail")]/ancestor::table[1]'
        '//*[contains(text(), "@")]/ancestor::ul[1]',
        '//*[contains(text(), "@")]',
    ]

    xpath_contact_list = [
        '//*[contains(text(), "contact")]/ancestor::div[contains(@class, "footer")][1]',
        '//*[contains(@class, "contact")]/ancestor::div[1]',
        # '//*[contains(text(), "contact")]/ancestor::div[1]',
        '//*[contains(@class, "contact")]',
    ]

    contacts_data = []

    # Find phone
    contacts_data.extend(find_by_xpath_list(xpath_phone_list, page_soup))

    # Find email
    contacts_data.extend(find_by_xpath_list(xpath_mail_list, page_soup))

    # Find address
    contacts_data.extend(find_by_xpath_list(xpath_address_list, page_soup))

    # Find contacts
    contacts_data.extend(find_by_xpath_list(xpath_contact_list, page_soup))

    return {
        "base_url": base_url,
        "contacts_url": url,
        "contacts_data": contacts_data,
    }


def get_contacts_data(contacts_dict, from_file=False):
    # If from_file == True
    if from_file:
        try:
            last_file_path = f"{ATTEMPT_DIR}contacts_data.json"
            return fgm.json_read(last_file_path)

        # If file doesn't exist
        except Exception as _ex:
            pm.error(f"Couldn't read from a file")
            return get_contacts_data(contacts_dict)

    # Create list [{base_url: url}, {} ...]
    contacts_url_list = [{
        base_url: url
    }
        for base_url, url in zip(contacts_dict.keys(), contacts_dict.values())
        if url is not None
    ]

    # Result json [{"base_url": url, "contacts_url": url, "contacts_data": data_str}, {} ...]
    contacts_data_json = []
    contacts_url_iterator = gm.UrlIterator(contacts_url_list, MAX_WORKERS)
    for contacts_url_part_list in contacts_url_iterator:

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {
                executor.submit(find_contacts_data, contacts_url, splash): contacts_url
                for contacts_url, splash in zip(contacts_url_part_list, splash_list)
            }

            # Process the results
            for future in as_completed(futures):
                contacts_url = futures[future]

                # Try to get data concurrently
                try:
                    res = future.result()
                    if res is not None:
                        contacts_data_json.append(res)

                except Exception as _ex:
                    pm.error(f"Error while executing '{contacts_url}': {_ex}")

                    failed_result = {
                        "base_url": [*contacts_url.keys()][0],
                        "contacts_url": [*contacts_url.values()][0],
                        "contacts_data": None
                    }
                    contacts_data_json.append(failed_result)
                    pm.error(f"Couldn't get a contacts url for: {contacts_url}")
                    time.sleep(20)

    fgm.json_rewrite(f"{ATTEMPT_DIR}contacts_data.json", contacts_data_json)
    return contacts_data_json


def parse_contacts_data(contacts_data):
    if contacts_data['contacts_data'] is not None:
        soup_list = [BeautifulSoup(str(x).replace("\\n", " ").replace("b'", '').replace("\\t", " "), 'lxml')
                     for x in contacts_data['contacts_data']]
        contacts_data_list = tuple(gm.clean_str(x.text.strip()) for x in soup_list)

        return {
            "base_url": contacts_data['base_url'],
            "contacts_url": contacts_data['contacts_url'],
            "contacts_data": contacts_data_list,
        }

    else:
        return None


def get_parsed_contacts_data(contacts_data_list):
    # TODO ThreadPoolExecutor module
    # Result json [{"base_url": url, "contacts_url": url, "contacts_data": data_str}, {} ...]
    parsed_contacts_data_json = []
    contacts_data_iterator = gm.UrlIterator(contacts_data_list, MAX_WORKERS)
    for contacts_data_part_list in contacts_data_iterator:

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {
                executor.submit(parse_contacts_data, contacts_data): contacts_data
                for contacts_data in contacts_data_part_list
            }

            # Process the results
            for future in as_completed(futures):
                contacts_data = futures[future]

                # Try to get data concurrently
                try:
                    res = future.result()
                    if res is not None:
                        parsed_contacts_data_json.append(res)

                except Exception as _ex:
                    pm.error(f"Error while executing '{contacts_data['base_url']}': {_ex}")

                    failed_result = {
                        "base_url": contacts_data['base_url'],
                        "contacts_url": contacts_data['contacts_url'],
                        "contacts_data": None
                    }
                    parsed_contacts_data_json.append(failed_result)
                    pm.error(f"Couldn't parse contacts data for: {contacts_data['base_url']}")
                    raise _ex

    fgm.json_rewrite(f"{ATTEMPT_DIR}parsed_contacts_data.json", parsed_contacts_data_json)
    return parsed_contacts_data_json


def get_non_processed_urls(attempt_dir):
    contacts_dict = fgm.json_read(f"{attempt_dir}contacts_dict.json")
    non_processed_url_list = []
    for key, value in zip(contacts_dict.keys(), contacts_dict.values()):
        if value is None:
            non_processed_url_list.append(key)

    contacts_data = fgm.json_read(f"{attempt_dir}contacts_data.json")
    for item in contacts_data:
        if (item.get("contacts_data") is None) or (item.get("contacts_data") == []):
            non_processed_url_list.append(item['base_url'])

    non_processed_url_list = clear_url_list(non_processed_url_list)
    return non_processed_url_list


# # ===== Iterations ================================================================================= Iterations =====
...
# # ===== Iterations ================================================================================= Iterations =====


def first_attempt(skip=False):
    if not skip:
        global ATTEMPT_DIR
        ATTEMPT_DIR = f"{DB_DATA_DIR}attempt_01/"
        if not os.path.exists(ATTEMPT_DIR):
            os.mkdir(ATTEMPT_DIR)

        # dh.recreate_dirs()
        fgm.remove_files_by_extension(dh.db_data, "html")

        # TODO: update key // update url_list
        url_list = get_search_url_list(from_file=True)

        # Get list of Contacts/About Us urls
        # TODO: first, check if there is "/contact" or "/about_us" etc
        contacts_dict = get_contacts_dict(url_list, from_file=True)

        # Get contacts data to future sorting
        # TODO: data mixed??
        contacts_data_list = get_contacts_data(contacts_dict, from_file=False)

        # Data mining
        parsed_contacts_data_json = get_parsed_contacts_data(contacts_data_list)


def second_attempt(skip=False):
    if not skip:
        global ATTEMPT_DIR
        ATTEMPT_DIR = f"{DB_DATA_DIR}attempt_02/"
        if not os.path.exists(ATTEMPT_DIR):
            os.mkdir(ATTEMPT_DIR)

        # Get all url for which there are no any contacts
        url_list = get_non_processed_urls(attempt_dir=f"{DB_DATA_DIR}attempt_01/")

        # Get list of Contacts/About Us urls
        # TODO: first, check if there is "/contact" or "/about_us" etc
        contacts_dict = get_contacts_dict(url_list, from_file=True)

        # Get contacts data to future sorting
        # TODO: data mixed??
        contacts_data_list = get_contacts_data(contacts_dict, from_file=True)
       
        # Data mining
        parsed_contacts_data_json = get_parsed_contacts_data(contacts_data_list)


def clean_data(filepath):
    contacts = fgm.json_read(filepath)
    clear_contacts = []
    for item in contacts:
        clear_contacts_item = []
        for x in item["contacts_data"]:
            clear_contacts_item.append(str(x).replace("\\", '').replace("b'", "").replace("'", ""))
        clear_contacts.append(
            {
                "base_url": item["base_url"],
                "contacts_url": item["contacts_url"],
                "contacts_data": clear_contacts_item,
            }
        )

    return clear_contacts


def build_prompt(raw_data):
    header = "Extract contact information from the string I provide. I need to get an email, phone number, and " \
                  "address if it is in the string." \
                  "\nString:\n"
    return f"{header}{raw_data}"


def nlp_by_gpt(contacts_data):
    gpt = ChatGPT()
    final_contacts_data = []
    for item, url_counter in zip(contacts_data, range(len(contacts_data))):
        try:
            final_contacts_item = []
            if item["contacts_data"] is not None:
                for x, counter in zip(item["contacts_data"], range(1, len(item["contacts_data"]) + 1)):
                    try:
                        # Sleeping before request ChatGPT
                        pm.info("Sleep 20s ...")
                        time.sleep(20)
                        gm.delete_last_print_lines()

                        start_request_time = datetime.datetime.utcnow()
                        response = gpt.chat_request(build_prompt(x))
                        final_contacts_item.append(response)
                        end_request_time = datetime.datetime.utcnow()
                        worktime = end_request_time - start_request_time

                        pm.info(f'{url_counter:>3}/{len(contacts_data)}: {item["base_url"]} '
                                f'{counter:>3}/{len(item["contacts_data"])}; Request time: {worktime}')

                    except Exception as _ex:
                        pm.error(f'url: {item["base_url"]}; part: {url_counter:>3}/{len(contacts_data)}; Error: {_ex}')
                final_contacts_data.append(
                    {
                        "base_url": item["base_url"],
                        "contacts_url": item["contacts_url"],
                        "contacts_data": final_contacts_item,
                    }
                )
        except Exception as _ex:
            pm.error(f"Hmm... What? Why? > {_ex}")

        fgm.json_rewrite(f"{DB_DATA_DIR}contacts_middle.json", final_contacts_data)

    return final_contacts_data


def extract_contacts_by_gpt():
    contacts_data = []
    filepath_attempt_01 = f"{DB_DATA_DIR}attempt_01/parsed_contacts_data.json"
    filepath_attempt_02 = f"{DB_DATA_DIR}attempt_02/parsed_contacts_data.json"

    contacts_data.extend(clean_data(filepath_attempt_01))
    contacts_data.extend(clean_data(filepath_attempt_02))

    final_contacts_data = nlp_by_gpt(contacts_data)

    fgm.json_rewrite(f"{DB_DATA_DIR}contacts.json", final_contacts_data)


# # ===== Start app =================================================================================== Start app =====
...
# # ===== Start app =================================================================================== Start app =====


def start_app():
    first_attempt(skip=True)

    second_attempt(skip=True)

    extract_contacts_by_gpt()


def anchor():
    pass


if __name__ == '__main__':
    start_app()
