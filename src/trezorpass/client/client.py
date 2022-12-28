import threading
import asyncio
import logging

from trezorlib.client import TrezorClient
from trezorlib.transport import Transport, get_transport

from trezorpass.client.ui import ManagerUI


class ExtendedTrezorClient(TrezorClient):
    def __init__(self, transport: Transport, ui: ManagerUI, **kwargs):
        self._lock = threading.Lock()
        self._healthcheck: asyncio.Task | None = None
        super().__init__(transport, ui, _init_device=False, **kwargs)

    def call_raw(self, msg):
        with self._lock:
            return super().call_raw(msg)

    def start_healthcheck(self, interval: float = 1):
        observer = asyncio.current_task()

        async def healthcheck_task():
            try:
                while self._healthcheck:
                    await asyncio.get_event_loop().run_in_executor(None, self.ping, "healthcheck")
                    await asyncio.sleep(interval)
            except Exception as e:
                observer.cancel()
                logging.exception("Client healthcheck has failed", exc_info=e)

        self._healthcheck = asyncio.get_event_loop().create_task(healthcheck_task())

    def clear_healthcheck(self):
        self._healthcheck = None

    def __enter__(self):
        self.init_device()
        self.start_healthcheck()
        return self

    def __exit__(self, *args):
        self.clear_healthcheck()
        self.end_session()


def get_default_client() -> ExtendedTrezorClient:
    """Creates default thread-safe client instance

    Returns:
        Instance of the thread-safe Trezor client

    Raises:
        TransportException: when client cannot be found
        Exception: when client initialization fails
    """
    transport = get_transport()
    ui = ManagerUI()
    return ExtendedTrezorClient(transport, ui)