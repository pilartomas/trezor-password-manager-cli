from InquirerPy.utils import color_print

PROMPT = "(trezor)"

PRIMARY_COLOR = "#00783d"

def prompt_print(message):
    color_print([("class:prompt", f"{PROMPT} "), ("class:message", message)], {"prompt": PRIMARY_COLOR})

def welcome():
    print("###################################")
    color_print([("class:padding", "### "), ("class:title", "Trezor Password Manager CLI"),("class:padding", " ###")], {"title": PRIMARY_COLOR})
    print("###################################")

def goodbye():
    color_print([("class:goodbye"), "Goodbye"], {"goodbye": PRIMARY_COLOR})