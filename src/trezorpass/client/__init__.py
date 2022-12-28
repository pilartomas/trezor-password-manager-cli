import asyncio
import logging

from trezorlib.client import TrezorClient
from trezorlib.transport import get_transport

from .client import ThreadSafeTrezorClient
from .ui import ManagerUI


class TrezorManager:
    def __init__(self, trezor_client: TrezorClient):
        self.client = trezor_client
        self._healthcheck: asyncio.Task | None = None

    def start_healthcheck(self, interval: float = 1):
        observer = asyncio.current_task()

        async def healthcheck_task():
            try:
                while self._healthcheck:
                    await asyncio.get_event_loop().run_in_executor(None, self.client.ping, "healthcheck")
                    await asyncio.sleep(interval)
            except Exception as e:
                observer.cancel()
                logging.exception("Client healthcheck has failed", exc_info=e)

        self._healthcheck = asyncio.get_event_loop().create_task(healthcheck_task())

    def clear_healthcheck(self):
        self._healthcheck = None

    def __enter__(self):
        self.client.init_device()
        self.start_healthcheck()
        return self.client

    def __exit__(self, *args):
        self.clear_healthcheck()
        self.client.end_session()


def get_default_client_manager():
    transport = get_transport()
    manager_ui = ManagerUI()
    trezor_client = ThreadSafeTrezorClient(transport, manager_ui, _init_device=False)
    return TrezorManager(trezor_client)
