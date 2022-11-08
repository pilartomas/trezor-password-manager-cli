import os

import appdirs

from InquirerPy.utils import color_print

APP_DIR = appdirs.user_data_dir('trezor-pass')

PRIMARY_COLOR = "#00783d"
SECONDARY_COLOR = "#f7931a"

os.environ["INQUIRERPY_STYLE_QUESTIONMARK"] = PRIMARY_COLOR
os.environ["INQUIRERPY_STYLE_ANSWERMARK"] = PRIMARY_COLOR
os.environ["INQUIRERPY_STYLE_ANSWER"] = SECONDARY_COLOR
os.environ["INQUIRERPY_STYLE_INPUT"] = SECONDARY_COLOR
os.environ["INQUIRERPY_STYLE_POINTER"] = SECONDARY_COLOR
os.environ["INQUIRERPY_STYLE_FUZZY_PROMPT"] = PRIMARY_COLOR

def prompt_trezor():
    print("Proceed on your trezor device")

def welcome():
    head = """####################################################
#                                                  #
#       #######                                    #
#     ##       ##                                  #
#    ##         ##                                 #
#    ##         ##                                 #
#  #################                               #
#  ##             ##                               #
#  ##             ##                               #
#  ##             ##  """
    text = "Trezor Password Manager CLI"
    tail = """  #
#  ##             ##                               #
#  ##             ##                               #
#  ###           ###                               #
#    ###       ###                                 #
#      #### ####                                   #
#         ###                                      #
#                                                  #
####################################################"""
    color_print([("class:banner", head), ("class:text", text), ("class:banner", tail)], {"banner": PRIMARY_COLOR, "text": SECONDARY_COLOR})

def goodbye():
    color_print([("class:padding", "##################### "), ("class:title", "Goodbye"),("class:padding", " ######################")], {"padding": PRIMARY_COLOR,"title": SECONDARY_COLOR})

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