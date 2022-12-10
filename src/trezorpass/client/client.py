import threading

from trezorlib.client import TrezorClient
from trezorlib.transport import Transport, get_transport

from .ui import ManagerUI


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


class SafeTrezorClient(TrezorClient):
    def __init__(self, transport: Transport, ui: ManagerUI, **kwargs):
        self._lock = threading.Lock()
        super().__init__(transport, ui, _init_device=False, **kwargs)

    def call_raw(self, msg):
        with self._lock:
            return super().call_raw(msg)

    def __enter__(self):
        self.init_device()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_session()