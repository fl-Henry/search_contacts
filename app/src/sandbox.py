import os
import sys
import time
import requests

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

# Load config data
if os.path.exists(".env"):
    config = dotenv_values(".env")
elif os.path.exists("./src/.env"):
    config = dotenv_values("./src/.env")
elif os.path.exists("./app/src/.env"):
    config = dotenv_values("./app/src/.env")
else:
    raise ImportError

# PrintMode instance
pm = gm.PrintMode(
    [
        "DEBUG",
        "WARNING",
        "ERROR",
        "INFO",
    ],
    timestamp_key=False
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
splash = SplashHdr(SPLASH_BASE_URL, SPLASH_PARAMS)

# Threads
MAX_WORKERS = int(config["MAX_WORKERS"])


url = "https://www.facebook.com/wholesalepartseurope/"
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
# url_list = []
# for country in countries[:3]:
#     query = f'"{country}" phone parts "wholesale" suppliers'
#     for pageno in [0, 1, 2]:
#         url = f"https://search.brave.com/search?q={query}&offset={pageno}&source=web"
#         pm.debug(f"request: {url}")
#         response = requests.get(url, headers=wgm.get_headers()).text
#         url_list.append(response)
#         fgm.text_rewrite(f"{DB_DATA_DIR}{country}_{pageno}_brave.html", response)


def parse_docker_inspect(file_path):
    docker_inspect = fgm.json_read(file_path)
    return docker_inspect[0]['NetworkSettings']['Networks']['app_default']['IPAddress']


def get_splash_ips(instances_num):
    splash_ips = []
    for splash_index in range(instances_num):
        file_path = f"{dh.temp}splash_{splash_index}.json"
        os.system(f"docker inspect app-splash_{splash_index}-1 > {file_path}")
        splash_ip = parse_docker_inspect(file_path)
        splash_ips.append({
            "ip": splash_ip,
            "name": f"app-splash_{splash_index}-1",
            "service_name": f"splash_{splash_index}",
            "index": splash_index,

        })

    return splash_ips


instances_num = 5

splash_ips = get_splash_ips(instances_num)

for splash_ip in splash_ips:
    ip_port = f"{splash_ip['ip']}:8050"
    pm.debug(f"ping splash_{splash_ip['index']}: {ip_port}")
    splash = SplashHdr(f"http://{ip_port}/render.html", SPLASH_PARAMS)
    try:
        response = splash.get_response_text("https://bits.debian.org/", splash_api_timeout=30)
        fgm.text_rewrite(f"{dh.temp}{splash_ip['name']}.html", response)
        pm.debug(f"ping success splash_{splash_ip['index']}: {splash_ip['ip']}:8050")
    except Exception as _ex:
        pm.error(f"ping failed splash_{splash_ip['index']}: {splash_ip['ip']}:8050 >", _ex)

        # Restart container
        pm.debug(dh.docker_compose_file)
        os.system(f"docker compose -f {dh.docker_compose_file} restart {splash_ip['service_name']}")
