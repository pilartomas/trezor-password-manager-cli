import threading

from trezorlib.client import TrezorClient
from trezorlib.transport import Transport, get_transport
from trezorlib.ui import ClickUI


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


def get_safe_client():
    """Creates default thread-safe client instance

    Returns:
        Instance of the thread-safe Trezor client

    Raises:
        TransportException: when client cannot be found
        Exception: when client initialization fails
    """
    transport = get_transport()
    ui = ClickUI()
    return SafeTrezorClient(transport, ui)
