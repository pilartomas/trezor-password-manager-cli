import os

from InquirerPy.utils import color_print
from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import FormattedText

PRIMARY_COLOR = "#00783d"
SECONDARY_COLOR = "#f7931a"

os.environ["INQUIRERPY_STYLE_QUESTIONMARK"] = PRIMARY_COLOR
os.environ["INQUIRERPY_STYLE_ANSWERMARK"] = PRIMARY_COLOR
os.environ["INQUIRERPY_STYLE_ANSWER"] = SECONDARY_COLOR
os.environ["INQUIRERPY_STYLE_INPUT"] = SECONDARY_COLOR
os.environ["INQUIRERPY_STYLE_POINTER"] = SECONDARY_COLOR
os.environ["INQUIRERPY_STYLE_FUZZY_PROMPT"] = PRIMARY_COLOR


def prompt_print(message: str, **kwargs):
    print_formatted_text(
        FormattedText([(PRIMARY_COLOR, "# "), ("class:message", message)]),
        **kwargs
    )


def prompt_print_pairs(pairs: list[tuple[str, str]]):
    color_print([(SECONDARY_COLOR, "#")])
    for (name, value) in pairs:
        color_print([
            (PRIMARY_COLOR, "# "),
            ("class:name", f"{name}: "),
            (SECONDARY_COLOR, value if value else "<empty>")
        ])
    color_print([(SECONDARY_COLOR, "#")])


def welcome():
    banner = """####################################################
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
    color_print(prepare_graphics(banner), {"graphics": PRIMARY_COLOR, "text": SECONDARY_COLOR})


def goodbye():
    message = """##################### Goodbye ######################"""
    color_print(prepare_graphics(message), {"graphics": PRIMARY_COLOR, "text": SECONDARY_COLOR})


def pin_guide():
    guide = """#
#       #######                #######       
#     ##       ##            ##       ##   
#    ##         ##          ##         ##  
#    ##         ##          ##         ##  
#  #################      #################
#  ##  Input PIN  ##      ##  Input PIN  ## 
#  ##             ##      ##             ##
#  ##    7 8 9    ##      ##    e r t    ##
#  ##    4 5 6    ##  or  ##    d f g    ##
#  ##    1 2 3    ##      ##    c v b    ##
#  ###           ###      ###           ###
#    ###       ###          ###       ###  
#      #### ####              #### ####    
#         ###                    ###
#"""
    color_print(prepare_graphics(guide), {"graphics": PRIMARY_COLOR, "text": SECONDARY_COLOR})


def confirm_guide():
    guide = """#
#       #######     
#     ##       ##   
#    ##         ##  
#    ##         ##  
#  #################
#  ##             ##
#  ##   Confirm   ##
#  ##             ##
#  ##             ##
#  ##  No    Yes  ##
#  ###           ###
#    ###       ###  
#      #### ####    
#         ###
#"""
    color_print(prepare_graphics(guide), {"graphics": PRIMARY_COLOR, "text": SECONDARY_COLOR})


def animate_dots(max_dots: int = 5):
    """Indefinitely keeps printing dots into the terminal, wrapping at specified value

    Args:
        max_dots: number of dots to wrap after
    """
    dots = 0
    while True:
        yield
        if dots == max_dots:
            print("\b \b" * dots, end="", flush=True)
            dots = 0
        else:
            print(".", end="", flush=True)
            dots += 1


def prepare_graphics(graphics: str,
                     graphics_characters: str = "#",
                     graphics_class: str = "graphics",
                     text_class: str = "text"):
    """Prepares ASCII graphics to be printed by color_print

    Args:
        graphics: ASCII graphics
        graphics_characters: String of characters that are considered to be visual only
        graphics_class: Class to be used for visual characters
        text_class: Class to be used for non-visual characters
    """
    result = []
    buffer = ""
    is_graphics = True
    for c in graphics:
        if c.isspace():
            buffer += c
        elif is_graphics and c not in graphics_characters:
            result.append((f"class:{graphics_class}", buffer))
            is_graphics = False
            buffer = c
        elif not is_graphics and c in graphics_characters:
            result.append((f"class:{text_class}", buffer))
            is_graphics = True
            buffer = c
        else:
            buffer += c
    result.append((f"class:{graphics_class if is_graphics else text_class}", buffer))
    return result
