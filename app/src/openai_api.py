import sys
import openai

from dotenv import dotenv_values

# Custom imports
import general_methods as gm
import files_general_methods as fgm


# # ===== Global variables ===================================================================== Global variables =====
...
# # ===== Global variables ===================================================================== Global variables =====


# Config file
config = dotenv_values(".env")


# # ===== Main part =================================================================================== Main part =====
...
# # ===== Main part =================================================================================== Main part =====


class ChatGPT:

    def __init__(self, api_key=None):
        if api_key is None:
            api_key = config["OPENAI_API_KEY"]

        openai.api_key = api_key

    @staticmethod
    def chat_request(prompt_str, temperature=0.8):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt_str}],
            temperature=temperature,
        )
        return response.choices[0].message.content

    @staticmethod
    def get_usage():
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": ''}],
        )
        gm.PrintMode.debug(response.usage)
        return response.usage


# # ===== EOF =============================================================================================== EOF =====
...
# # ===== EOF =============================================================================================== EOF =====


def main():
    gpt = ChatGPT()
    gpt.get_usage()


if __name__ == '__main__':
    main()
