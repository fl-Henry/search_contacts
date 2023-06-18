import general_methods as gm
import files_general_methods as fgm


url = "https://europespares.com/2021/04/14/phone-parts-europe/"
url = "https://repairbase.eu/contact-us/"
print(gm.url_to_base_url(url))


data = {
    "key": "value",
    "key1": None,
}
fgm.json_rewrite("./test.json", data)