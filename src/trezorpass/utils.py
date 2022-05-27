import os

from InquirerPy.utils import color_print

PROMPT = "(trezor)"

PRIMARY_COLOR = "#00783d"
SECONDARY_COLOR = "#f7931a"

os.environ["INQUIRERPY_STYLE_QUESTIONMARK"] = PRIMARY_COLOR
os.environ["INQUIRERPY_STYLE_ANSWERMARK"] = PRIMARY_COLOR
os.environ["INQUIRERPY_STYLE_ANSWER"] = SECONDARY_COLOR
os.environ["INQUIRERPY_STYLE_INPUT"] = SECONDARY_COLOR
os.environ["INQUIRERPY_STYLE_POINTER"] = SECONDARY_COLOR
os.environ["INQUIRERPY_STYLE_FUZZY_PROMPT"] = PRIMARY_COLOR

def prompt_print(message, prompt=PROMPT, prompt_color=PRIMARY_COLOR):
    color_print([("class:prompt", f"{prompt} "), ("class:message", message)], {"prompt": prompt_color})

def prompt_trezor():
    prompt_print("Proceed on your trezor device")

def welcome():
    welcome = """####################################################
#                                                  #
#       #######                                    #
#     ##       ##                                  #
#    ##         ##                                 #
#    ##         ##                                 #
#  #################                               #
#  ##             ##                               #
#  ##             ##                               #
#  ##             ##  Trezor Password Manager CLI  #
#  ##             ##                               #
#  ##             ##                               #
#  ###           ###                               #
#    ###       ###                                 #
#      #### ####                                   #
#         ###                                      #
#                                                  #
####################################################"""
    print(welcome)

def goodbye():
    color_print([("class:padding", "##################### "), ("class:title", "Goodbye"),("class:padding", " ######################")], {"title": PRIMARY_COLOR})

def animate_dots(max_dots: int):
    dots = 0
    while True:
        yield
        if dots == max_dots:
            print("\b \b" * dots, end="", flush=True)
            dots = 0
        else:
            print(".", end="", flush=True)
            dots += 1