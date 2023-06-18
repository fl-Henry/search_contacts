# general_methods.py
import os
import sys
import random

from math import ceil
from threading import Lock, Thread
from datetime import datetime, timedelta, date
from concurrent.futures import ThreadPoolExecutor, as_completed


# # ===== General Methods ======================================================================= General Methods =====
...
# # ===== General Methods ======================================================================= General Methods =====


class PrintModeSingletonMeta(type):
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


class PrintMode(metaclass=PrintModeSingletonMeta):

    mode_list = [
        "DEBUG",
        "WARNING",
        "ERROR",
        "INFO",
    ]
    max_len = max([len(x) for x in mode_list])

    def __init__(self, print_mode: list = None, timestamp_key=False):
        if print_mode is None:
            self.mode = self.mode_list
        else:
            for mode_item in print_mode:
                if mode_item not in self.mode_list:
                    raise ValueError("[ERROR] PrintMode.__init__: Wrong print mode")
            self.mode = print_mode

        self.timestamp = timestamp_key

    def print(self, mode, *message, color=None):
        message = " ".join([str(x) for x in message])
        stdout = ""
        if mode in self.mode:
            if color is not None:
                stdout += f"{color}[{mode:^{self.max_len}}]{Tags.ResetAll} "
            else:
                stdout += f"[{mode:^{self.max_len}}] "

            if self.timestamp:
                stdout += f"{get_timestamp()} "
            print(f"{stdout}:: {message}")

    @classmethod
    def debug(cls, *message):
        cls.print(cls(), 'DEBUG', *message, color=Tags.Blue)

    @classmethod
    def warning(cls, *message):
        cls.print(cls(), 'WARNING', *message, color=Tags.Yellow + Tags.Bold)

    @classmethod
    def error(cls, *message):
        cls.print(cls(), 'ERROR', *message, color=Tags.Red + Tags.Bold)

    @classmethod
    def info(cls, *message):
        cls.print(cls(), 'INFO', *message)


class Tags:
    # Reset
    ResetAll = "\033[0m"
    ResetBold = "\033[21m"
    ResetDim = "\033[22m"
    ResetUnderlined = "\033[24m"
    ResetBlink = "\033[25m"
    ResetReverse = "\033[27m"
    ResetHidden = "\033[28m"

    # Mode
    Bold = "\033[1m"
    Dim = "\033[2m"
    Underlined = "\033[4m"
    Blink = "\033[5m"
    Reverse = "\033[7m"
    Hidden = "\033[8m"

    # Text color
    Default = "\033[39m"
    Black = "\033[30m"
    Red = "\033[31m"
    Green = "\033[32m"
    Yellow = "\033[33m"
    Blue = "\033[34m"
    Magenta = "\033[35m"
    Cyan = "\033[36m"
    LightGray = "\033[37m"
    DarkGray = "\033[90m"
    LightRed = "\033[91m"
    LightGreen = "\033[92m"
    LightYellow = "\033[93m"
    LightBlue = "\033[94m"
    LightMagenta = "\033[95m"
    LightCyan = "\033[96m"
    White = "\033[97m"

    # Background color
    BackgroundDefault = "\033[49m"
    BackgroundBlack = "\033[40m"
    BackgroundRed = "\033[41m"
    BackgroundGreen = "\033[42m"
    BackgroundYellow = "\033[43m"
    BackgroundBlue = "\033[44m"
    BackgroundMagenta = "\033[45m"
    BackgroundCyan = "\033[46m"
    BackgroundLightGray = "\033[47m"
    BackgroundDarkGray = "\033[100m"
    BackgroundLightRed = "\033[101m"
    BackgroundLightGreen = "\033[102m"
    BackgroundLightYellow = "\033[103m"
    BackgroundLightBlue = "\033[104m"
    BackgroundLightMagenta = "\033[105m"
    BackgroundLightCyan = "\033[106m"
    BackgroundWhite = "\033[107m"

    def print_tags(self):
        mode = {
            "Bold": self.Bold,
            "Dim": self.Dim,
            "Underlined": self.Underlined,
            "Blink": self.Blink,
            "Reverse": self.Reverse,
            "Hidden": self.Hidden,
        }
        txt = {
            "Default": self.Default,
            "Black": self.Black,
            "Red": self.Red,
            "Green": self.Green,
            "Yellow": self.Yellow,
            "Blue": self.Blue,
            "Magenta": self.Magenta,
            "Cyan": self.Cyan,
            "LightGray": self.LightGray,
            "DarkGray": self.DarkGray,
            "LightRed": self.LightRed,
            "LightGreen": self.LightGreen,
            "LightYellow": self.LightYellow,
            "LightBlue": self.LightBlue,
            "LightMagenta": self.LightMagenta,
            "LightCyan": self.LightCyan,
            "White": self.White,
        }
        bg = {
            "Default": self.BackgroundDefault,
            "Black": self.BackgroundBlack,
            "Red": self.BackgroundRed,
            "Green": self.BackgroundGreen,
            "Yellow": self.BackgroundYellow,
            "Blue": self.BackgroundBlue,
            "Magenta": self.BackgroundMagenta,
            "Cyan": self.BackgroundCyan,
            "LightGray": self.BackgroundLightGray,
            "DarkGray": self.BackgroundDarkGray,
            "LightRed": self.BackgroundLightRed,
            "LightGreen": self.BackgroundLightGreen,
            "LightYellow": self.BackgroundLightYellow,
            "LightBlue": self.BackgroundLightBlue,
            "LightMagenta": self.BackgroundLightMagenta,
            "LightCyan": self.BackgroundLightCyan,
            "White": self.BackgroundWhite,
        }
        max_mode = max([len(x) for x in mode.keys()])
        max_txt = max([len(x) for x in txt.keys()])
        max_bg = max([len(x) for x in bg.keys()])

        for txt_key in txt.keys():
            for bg_key in bg.keys():
                for mode_key in mode.keys():
                    print(f"Sample text: {mode[mode_key]}{txt[txt_key]}{bg[bg_key]} Sample text {self.ResetAll}"
                          f" {txt_key:<{max_txt}} + Background{bg_key:<{max_bg}} + {mode_key:<{max_mode}}")


def if_iterable(obj):
    try:
        obj_to_try = iter(obj)
    except TypeError as te:
        return False
    return True


def concurrent_func(func, list_of_args, workers_num=20):
    results_data = []
    with ThreadPoolExecutor(max_workers=workers_num) as executor:
        futures = {executor.submit(func, *args): args for args in list_of_args}

        # Process the results as they become available
        for future in as_completed(futures):
            args = futures[future]
            try:
                res = future.result()
                if res is not None:
                    results_data.extend(res)
            except Exception as _ex:
                print(f"Error while executing '{args}': {_ex}")


# # ===== Terminal Methods ===================================================================== Terminal Methods =====
...
# # ===== Terminal Methods ===================================================================== Terminal Methods =====


def delete_last_print_lines(n=1):
    # print("Entering to loop")
    # delete_last_print_lines()
    # print(f"{list_index}/{len(symbols_list)}")
    CURSOR_UP_ONE = '\x1b[1A'
    ERASE_LINE = '\x1b[2K'
    for _ in range(n):
        sys.stdout.write(CURSOR_UP_ONE)
        sys.stdout.write(ERASE_LINE)
        print("", end="\r")


def notification(message, counter_to_delete=1):
    # TODO: notifications class

    answer = ""
    counter_to_delete += 1
    wrong_counter_to_delete = counter_to_delete + 1
    while len(answer) == 0:
        try:
            print(message)
            print("Do you want to continue? (Y/N or 'exit'): ", end="")
            try:
                answer = str(input())
            except KeyboardInterrupt:
                print()
                raise KeyboardInterrupt
            except:
                delete_last_print_lines(counter_to_delete)
                answer = ""
                counter_to_delete = wrong_counter_to_delete
                print("Wrong input")

            if ("exit" in answer.lower()) or (answer.lower() == "n"):
                print("EXIT")
                sys.exit()
            elif answer.lower() == "y":
                delete_last_print_lines(counter_to_delete)
                answer = "Y"
                continue
            else:
                delete_last_print_lines(counter_to_delete)
                answer = ""
                counter_to_delete = wrong_counter_to_delete
                print("Wrong input")

        except KeyboardInterrupt:
            print("EXIT")
            sys.exit()


# # ===== String Methods ========================================================================= String Methods =====
...
# # ===== String Methods ========================================================================= String Methods =====


def remove_repeated_char(string_to_remove, char=" "):
    key_to_exit = False
    infinity_loop_counter = 0
    while not key_to_exit:
        key_to_exit = True
        for char_index in range(len(string_to_remove)):
            if string_to_remove[char_index:char_index + 2] == char * 2:

                # Repeat the loop for 3 and more repeated chars
                key_to_exit = False

                # Count repeated chars
                end_char_index = 0
                for last_char_index in range(len(string_to_remove[char_index:])):
                    if string_to_remove[char_index + last_char_index] != char:
                        end_char_index = last_char_index
                        break

                string_to_remove = string_to_remove[:char_index] + string_to_remove[char_index + end_char_index - 1:]

        # Checking if the loop is an infinite one
        if infinity_loop_counter < 10_000:
            infinity_loop_counter += 1
        else:
            raise Exception("[ERROR] remove_repeated_char > infinity_loop_counter > 10_000")

    return string_to_remove


def clean_str(original_string):
    return remove_repeated_char(original_string.replace("\r", " ").replace("\n", " "))


def find_number_indexes(in_string):
    in_list = [str(x) for x in range(10)]
    for start_num_index in range(len(in_string)):
        if in_string[start_num_index] in in_list:

            # Count last number in the sequence
            last_num_index = start_num_index
            for last_char_ind in range(start_num_index, len(in_string)):
                if in_string[last_char_ind] not in in_list:
                    last_num_index = last_char_ind
                    break

            return start_num_index, last_num_index


def find_char_index(in_string, char):
    for index in range(len(in_string)):
        if in_string[index] == char:
            return index
    return None


def find_all_chars(main_str, char):
    char_indexes_list = []
    for index in range(len(main_str)):
        if main_str[index] == char:
            char_indexes_list.append(index)

    return char_indexes_list


def find_string_indexes(main_string, find_string):
    """
        Finds first occurrence and returns start and end index of string
    :param main_string:     | string that probably contain find_string
    :param find_string:     | string that probably may be in main_string
    :return: [first_index, last_index] or None
    """
    for index in range(len(main_string) - len(find_string) + 1):
        if main_string[index:index + len(find_string)] == find_string:
            return index, index + len(find_string)
    return None


def find_all_strings(main_string, find_string):
    """
        Finds all occurrences and returns list of indexes (start and end index of string)
    :param main_string:     | string that probably contain find_string
    :param find_string:     | string that probably may be in main_string
    :return: [[first_index, last_index], ...]
    """
    list_to_return = []
    last_char = 0
    max_index = len(main_string)
    while last_char < max_index:
        indexes = find_string_indexes(main_string, find_string)
        if indexes is not None:
            main_string = main_string[indexes[1]:]
            indexes = [x + last_char for x in indexes]
            list_to_return.append(indexes)
            last_char = indexes[1]
        else:
            break
    return list_to_return


def str_equals_str(str_1, str_2):
    if len(str_1) != len(str_2):
        print("len:", len(str_1), len(str_2))
        return False

    for char_1, char_2 in zip(str_1, str_2):
        if char_1 != char_2:
            print("char:", char_1, char_2)
            return False

    return True


# # ===== URLs Methods ============================================================================= URLs Methods =====
...
# # ===== URLs Methods ============================================================================= URLs Methods =====


class UrlArrayIterator:
    def __init__(self, url_array, count_step):
        self.url_array = url_array
        self.step = count_step
        self.current_index = 0
        self.next_index = 0
        self.parts_num = ceil(max([len(x) for x in url_array]) / self.step)

    def __next__(self):
        self.current_index = self.next_index
        self.next_index += self.step
        stop_iter_key = True
        array_to_return = []
        for url_list in self.url_array:
            if self.current_index <= len(url_list) - 1:
                stop_iter_key = False
                if self.next_index <= len(url_list) - 1:
                    array_to_return.append(url_list[self.current_index:self.next_index])
                else:
                    array_to_return.append(url_list[self.current_index:])
            else:
                array_to_return.append([])

        if stop_iter_key:
            raise StopIteration
        else:
            return array_to_return

    def __iter__(self):
        self.current_index = 0
        self.next_index = 0
        return self


class UrlIterator:
    def __init__(self, url_list, count_step):
        self.url_list = url_list
        self.count_step = count_step
        self.current_index = 0
        self.next_index = 0
        self.last_index = len(url_list) - 1
        self.parts = self.last_index // self.count_step + 1

    def __next__(self):
        self.current_index = self.next_index
        if self.current_index <= self.last_index:
            self.next_index += self.count_step
            if self.next_index <= self.last_index:
                return self.url_list[self.current_index:self.next_index]
            else:
                return self.url_list[self.current_index:]
        else:
            raise StopIteration

    def __iter__(self):
        self.current_index = 0
        self.next_index = 0
        return self


def url_to_name(file_url, iter_count=1):
    input_file_url = file_url
    file_name = file_url
    process_url = file_url
    error_counter = 0
    while iter_count > 0:

        # Checking infinite loop
        error_counter += 1
        if error_counter > 8000:
            print("[ERROR] url_to_name > infinite loop")
            print(input_file_url)
            raise LookupError

        # Method logic
        if process_url[-1] == '/':
            process_url = process_url[:-1]
        for _ in range(1, len(process_url)):
            char = process_url[-1]
            if char == '/':
                file_name = file_url[len(process_url):]
                file_url = process_url[:-1]
                iter_count -= 1
                break
            else:
                process_url = process_url[:-1]
    return file_name


def url_parent(file_url, iter_count=1):
    input_file_url = file_url
    parent_url = file_url
    process_url = file_url
    error_counter = 0
    while iter_count > 0:

        # Checking infinite loop
        error_counter += 1
        if error_counter > 8000:
            print("[ERROR] url_parent > infinite loop")
            print(input_file_url)
            raise LookupError

        # Method logic
        if process_url[-1] == '/':
            process_url = process_url[:-1]
        for _ in range(1, len(process_url)):
            char = process_url[-1]
            if char == '/':
                parent_url = process_url
                iter_count -= 1
                break
            else:
                process_url = process_url[:-1]

    return parent_url


def repair_url(url, base_url):

    if url[:2] == "//":
        url = f"http://{url[3:]}"
    elif url[0] == "/":
        url = f"{base_url[:-1]}{url}"
    elif url[:4] != "http":
        url = f"{base_url}{url}"

    return url


def url_to_base_url(url):

    slash_counter = 3
    base_url = ""
    for char in url:

        if char == "/":
            slash_counter -= 1
        base_url += char

        if slash_counter == 0:
            break

    return base_url


# # ===== Date Methods ============================================================================= Date Methods =====
...
# # ===== Date Methods ============================================================================= Date Methods =====


def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def dates_between(start_date, end_date=None):
    """
    :param start_date: tuple[int, int, int]     | (31, 12, 2023)
    :param end_date: tuple[int, int, int]       | (31, 12, 2023) or None for today
    :return: list[tuple[int, int, int]]
    """
    start_date = date(start_date[2], start_date[1], start_date[0])

    if end_date is None:
        end_date = [int(x) for x in str(datetime.today().strftime("%d-%m-%Y")).split("-")]
    end_date = date(end_date[2], end_date[1], end_date[0])

    delta = end_date - start_date

    dates_between_list = []
    for i in range(delta.days + 1):
        day = start_date + timedelta(days=i)
        dates_between_list.append([int(x) for x in str(day.strftime("%d-%m-%Y")).split("-")])

    return dates_between_list


def random_dd_mm_yyy(start_date, end_date: tuple[int, int, int] = None):
    if end_date is None:
        end_date = datetime.today()
    else:
        if len(end_date) == 3:
            end_date = datetime(year=end_date[2], month=end_date[1], day=end_date[0])
        else:
            raise ValueError

    start_date = datetime(year=start_date[2], month=start_date[1], day=start_date[0])
    random_date = start_date + timedelta(seconds=random.randint(0, int((end_date - start_date).total_seconds())))

    dd = int(str(random_date.strftime("%d")))
    mm = int(str(random_date.strftime("%m")))
    yyyy = int(str(random_date.strftime("%Y")))
    return dd, mm, yyyy


if __name__ == '__main__':
    Tags().print_tags()
    print()
    pm = PrintMode(timestamp_key=True)
    text = "Message"
    pm.info(text)
    pm.debug(text)
    pm.warning(text)
    pm.error(text)
