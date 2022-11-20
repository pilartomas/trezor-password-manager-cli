import getpass
import threading
from typing import Optional, Union

from trezorlib import messages
from trezorlib.client import TrezorClient, MAX_PIN_LENGTH
from trezorlib.exceptions import Cancelled
from trezorlib.messages import PinMatrixRequestType
from trezorlib.transport import Transport, get_transport
from trezorlib.ui import ClickUI, PIN_MATRIX_DESCRIPTION

from trezorpass.utils import pin_guide, confirm_guide


class SafeTrezorClient(TrezorClient):
    def __init__(self, transport: Transport, ui: ClickUI, **kwargs):
        self._lock = threading.Lock()
        super().__init__(transport, ui, **kwargs)

    def open(self):
        with self._lock:
            return super().open()

    def call_raw(self, msg):
        with self._lock:
            return super().call_raw(msg)


class ManagerUI:
    @staticmethod
    def button_request(br: messages.ButtonRequest) -> None:
        confirm_guide()

    @staticmethod
    def get_pin(code: Optional[PinMatrixRequestType]) -> str:
        pin_guide()
        try:
            pin = getpass.getpass("Please enter PIN: ")
        except KeyboardInterrupt:
            raise Cancelled

        if all(d in "cvbdfgert" for d in pin):
            pin = pin.translate(str.maketrans("cvbdfgert", "123456789"))

        if any(d not in "123456789" for d in pin):
            print(
                "The value may only consist of digits 1 to 9 or letters cvbdfgert."
            )
        elif len(pin) > MAX_PIN_LENGTH:
            print(f"The value must be at most {MAX_PIN_LENGTH} digits in length.")
        else:
            return pin

    @staticmethod
    def get_passphrase(available_on_device: bool) -> Union[str, object]:
        return ""


def get_safe_client():
    """Creates default thread-safe client instance

    Returns:
        Instance of the thread-safe Trezor client

    Raises:
        TransportException: when client cannot be found
        Exception: when client initialization fails
    """
    transport = get_transport()
    ui = ManagerUI()
    return SafeTrezorClient(transport, ui)
