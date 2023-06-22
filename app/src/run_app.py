# run_app.py
import os
import sys
import time

from bs4 import BeautifulSoup
from dotenv import dotenv_values
from concurrent.futures import ThreadPoolExecutor, as_completed
from jinja2 import Environment, FileSystemLoader

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
        "temp": dh.temp,
    }
)
dh.dirs_to_remove.update(
    {
        "temp": dh.temp,
    }
)

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

# Splash config
SPLASH_BASE_URL = config['SPLASH_BASE_URL']
SPLASH_PARAMS = {
    "wait": config['SPLASH_PARAMS_WAIT'],
    "timeout": config['SPLASH_PARAMS_TIMEOUT'],
    "resource_timeout": config['REQUEST_TIMEOUT'],
    "images": config['IMAGES'],
}


# # ===== App logic =================================================================================== App logic =====
...
# # ===== App logic =================================================================================== App logic =====


def get_splash_instance():
    splash = SplashHdr(SPLASH_BASE_URL, SPLASH_PARAMS)


def create_docker_compose_yaml(instances_number):
    environment = Environment(loader=FileSystemLoader(dh.templates))
    template = environment.get_template("docker-compose.yaml")

    filename = f"{dh.base_dir}docker-compose.yaml"
    content = template.render(
        instances_number=instances_number
    )

    with open(filename, mode="w", encoding="utf-8") as message:
        message.write(content)
        pm.info(f"Docker compose config file created: {filename}")


def parse_docker_inspect(file_path):
    docker_inspect = fgm.json_read(file_path)
    return docker_inspect[0]['NetworkSettings']['Networks']['app_default']['IPAddress']


def get_splash_containers_data(instances_num):
    splash_containers_data = []
    for splash_index in range(instances_num):
        file_path = f"{dh.temp}splash_{splash_index}.json"
        os.system(f"docker inspect app-splash_{splash_index}-1 > {file_path}")
        splash_ip = parse_docker_inspect(file_path)
        splash_containers_data.append({
            "ip": f"{splash_ip}:806{splash_index}",
            "name": f"app-splash_{splash_index}-1",
            "service_name": f"splash_{splash_index}",
            "index": splash_index,

        })

    fgm.json_rewrite(f"{dh.temp}splash_containers_data.json", splash_containers_data)
    return splash_containers_data


def check_splash_containers(splash_containers_data):
    for splash_data in splash_containers_data:
        ip_port = f"{splash_data['ip']}"
        pm.debug(f"ping splash_{splash_data['index']}: {ip_port}")
        splash = SplashHdr(f"http://{ip_port}/render.html", SPLASH_PARAMS)
        try:
            response = splash.get_response_text("https://localhost/", splash_api_timeout=int(config["SPLASH_API_TIMEOUT"]))
            # response = splash.get_response_text("https://google.com/", splash_api_timeout=int(config["SPLASH_API_TIMEOUT"]))
            fgm.text_rewrite(f"{dh.temp}{splash_data['name']}.html", response)
            pm.debug(f"ping success splash_{splash_data['index']}: {splash_data['ip']}")
        except Exception as _ex:
            pm.error(f"ping failed splash_{splash_data['index']}: {splash_data['ip']} >", _ex)

            # Restart container
            pm.debug(dh.docker_compose_file)
            os.system(f"docker compose -f {dh.docker_compose_file} restart {splash_data['service_name']}")


# # ===== Start app =================================================================================== Start app =====
...
# # ===== Start app =================================================================================== Start app =====


def start_app():
    dh.create_dirs()
    instances_num = int(config["INSTANCES_NUMBER"])

    create_docker_compose_yaml(instances_num)

    os.system("docker compose up &")
    time.sleep(30)

    splash_containers_data = get_splash_containers_data(instances_num)

    try:
        while True:
            check_splash_containers(splash_containers_data)
            time.sleep(120)
    except KeyboardInterrupt:
        pm.info("\nEXIT ...")

    dh.remove_dirs()


if __name__ == '__main__':
    start_app()
