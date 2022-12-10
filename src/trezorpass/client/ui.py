import getpass
from typing import Optional, Union

from trezorlib import messages
from trezorlib.exceptions import Cancelled
from trezorlib.messages import PinMatrixRequestType
from trezorlib.client import MAX_PIN_LENGTH

from trezorpass.utils import pin_guide, confirm_guide, prompt_print


class ManagerUI:
    @staticmethod
    def button_request(br: messages.ButtonRequest) -> None:
        confirm_guide()

    @staticmethod
    def get_pin(code: Optional[PinMatrixRequestType]) -> str:
        pin_guide()
        try:
            prompt_print("", end="")
            pin = getpass.getpass("Please enter PIN: ")
        except KeyboardInterrupt:
            raise Cancelled

        if all(d in "cvbdfgert" for d in pin):
            pin = pin.translate(str.maketrans("cvbdfgert", "123456789"))

        if any(d not in "123456789" for d in pin):
            prompt_print(
                "The value may only consist of digits 1 to 9 or letters cvbdfgert."
            )
            raise Cancelled
        elif len(pin) > MAX_PIN_LENGTH:
            prompt_print(f"The value must be at most {MAX_PIN_LENGTH} digits in length.")
            raise Cancelled
        else:
            return pin

    @staticmethod
    def get_passphrase(available_on_device: bool) -> Union[str, object]:
        return ""
