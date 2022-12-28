import threading

from trezorlib.client import TrezorClient
from trezorlib.transport import Transport
from trezorlib.ui import TrezorClientUI


class ThreadSafeTrezorClient(TrezorClient):
    def __init__(self, transport: Transport, ui: TrezorClientUI, **kwargs):
        self._lock = threading.Lock()
        super().__init__(transport, ui, **kwargs)

    def call_raw(self, msg):
        with self._lock:
            return super().call_raw(msg)
