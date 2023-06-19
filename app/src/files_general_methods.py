# files_general_methods.py
import os
import sys
import csv
import json
import shutil

from threading import Lock, Thread

# Custom imports
import general_methods as gm

# # ===== Directories =============================================================================== Directories =====
...
# # ===== Directories =============================================================================== Directories =====


class DirectoriesHandlerSingletonMeta(type):
    """
    This is a thread-safe implementation of Singleton.
    """

    _instances = {}

    _lock: Lock = Lock()
    """
    We now have a lock object that will be used to synchronize threads during
    first access to the Singleton.
    """

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """

        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class DirectoriesHandler(metaclass=DirectoriesHandlerSingletonMeta):

    def __init__(self):
        base_path = str(__file__)[:len(__file__) - len(os.path.basename(str(__file__))) - 1]

        # Dirs
        self.base_dir = f"{gm.url_parent(base_path)}"
        self.src = f"{self.base_dir}src/"
        self.db_data = f"{self.base_dir}db_data/"
        self.temp = f"{self.base_dir}temp/"
        self.for_tests = f"{self.base_dir}for_tests/"
        self.templates = f"{self.base_dir}templates/"

        self.docker_compose_file = f"{self.base_dir}docker-compose.yaml"

        self.dirs = {
            # "base_dir": ,
            # "data": ,
            # "temp_dir": ,
        }

        self.dirs_to_remove = {
            # "data": self.dirs["data"],
        }

    def __str__(self):
        stdout = ""

        # Add dirs in stdout
        if len(self.dirs) > 0:
            stdout = f"\nDirs: "
            for key in self.dirs.keys():
                stdout += f"\n  {key:<16}: {self.dirs[key]}"

        # Add dirs_to_delete in stdout
        if len(self.dirs_to_remove) > 0:
            stdout += f"\nDirs to delete: "
            for key in self.dirs_to_remove.keys():
                stdout += f"\n  {key:<16}: {self.dirs_to_remove[key]}"

        return stdout

    # Create all dirs
    def create_dirs(self):
        for key in self.dirs.keys():
            if not os.path.exists(self.dirs[key]):
                os.mkdir(self.dirs[key])

    # Delete all dirs
    def remove_dirs(self):
        for key in self.dirs_to_remove.keys():
            if os.path.exists(self.dirs_to_remove[key]):
                shutil.rmtree(self.dirs_to_remove[key], ignore_errors=True)

    def recreate_dirs(self):
        self.remove_dirs()
        self.create_dirs()

    def get_file_names(self, path=None, recursive=False):
        if path is None:
            path = self.base_dir

        file_name_list = []
        for (dirpath, dirnames, filenames) in os.walk(path):
            file_name_list.extend(filenames)
            if not recursive:
                break

        return file_name_list

    def get_dir_paths(self, path=None, recursive=False):
        if path is None:
            path = self.base_dir

        dir_path_list = []
        for (dirpath, dirnames, filenames) in os.walk(path):
            dir_path_list.append(dirpath)
            if not recursive:
                break

        return dir_path_list

    def get_dir_names(self, path=None, recursive=False):
        if path is None:
            path = self.base_dir

        dir_name_list = []
        for (dirpath, dirnames, filenames) in os.walk(path):
            dir_name_list.extend(dirnames)
            if not recursive:
                break

        return dir_name_list


def remove_files_by_extension(path, extension, recursive=False):
    for (dirpath, dirnames, filenames) in os.walk(path):
        for filename in filenames:
            if f".{extension}" == filename[-(len(extension) + 1):]:
                os.remove(f"{dirpath}{filename}")

        if not recursive:
            break


# # ===== JSON ============================================================================================= JSON =====
...
# # ===== JSON ============================================================================================= JSON =====


class JSONFile:

    # TODO: class json_file
    #           - append
    #           - rewrite
    #           - write
    #           - create
    #           - read
    #           - delete
    #           - convert? to csv
    #           - silent

    def __init__(self, json_data, filepath):
        self.json_data = json_data
        self.filepath = filepath
        self.indent = 4

    def read(self):
        return json_read(self.filepath)

    def rewrite(self):
        json_rewrite(
            filepath=self.filepath,
            json_data=self.json_data,
            indent=self.indent
        )


def json_read(filepath):
    with open(filepath, "r") as file:
        json_data = json.loads(file.read())
        return json_data


def json_rewrite(filepath, json_data=None, indent=4):
    try:
        with open(filepath, "w") as file:
            file.write(json.dumps(json_data, indent=indent))
            gm.PrintMode.info("Saved to:", filepath)

    except Exception as _ex:
        gm.PrintMode.error("Not saved:", _ex)


# # ===== CSV =============================================================================================== CSV =====
...
# # ===== CSV =============================================================================================== CSV =====


# def save_to_csv(product_data_list, file_path=None):
#     # Crate DataFrame
#     to_csv_df = pd.DataFrame(
#         product_data_list
#     )
#
#     # Move columns
#     to_csv_df = move_columns(to_csv_df)
#
#     # Generate filepath
#     timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
#     if file_path is None:
#         file_path = f"./csvs/{timestamp}_{DOMAIN_NAME}_products_data.csv"
#
#     # Save to csv
#     to_csv_df.to_csv(file_path, sep=';', encoding='utf-8')
#     print(f"\n{gm.Tags.LightYellow}Saved to: {file_path}{gm.Tags.ResetAll}")


# # ===== Text Files ================================================================================= Text Files =====
...
# # ===== Text Files ================================================================================= Text Files =====


def text_rewrite(filepath, text_data=None):
    try:
        with open(filepath, "w") as file:
            file.write(text_data)
            gm.PrintMode.info("Saved to:", filepath)

    except Exception as _ex:
        gm.PrintMode.error("Not saved:", _ex)
