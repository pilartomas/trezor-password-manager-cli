import asyncio
import logging
from contextlib import contextmanager

from trezorlib.transport import get_transport

from .client import ThreadSafeTrezorClient
from .ui import ManagerUI


@contextmanager
def get_default_client_manager():
    transport = get_transport()
    manager_ui = ManagerUI()
    trezor_client = ThreadSafeTrezorClient(transport, manager_ui, _init_device=False)

    observer = asyncio.current_task()

    async def healthcheck():
        try:
            while healthcheck_task:
                await asyncio.get_event_loop().run_in_executor(None, trezor_client.ping, "healthcheck")
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            observer.cancel()
            logging.exception("Client healthcheck has failed", exc_info=e)

    try:
        trezor_client.init_device()
        healthcheck_task = asyncio.get_event_loop().create_task(healthcheck())
        yield trezor_client
    finally:
        if healthcheck_task:
            healthcheck_task.cancel()
        trezor_client.end_session()
