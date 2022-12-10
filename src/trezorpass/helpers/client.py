import asyncio

from trezorlib.client import TrezorClient
from trezorlib.transport import TransportException

from ..client import get_safe_client
from ..utils import animate_dots, prompt_print


healthcheck_tasks = set()


async def get_client() -> TrezorClient:
    """Waits for the Trezor client to connect

    Returns:
        The connected Trezor client

    Raises:
        KeyboardInterrupt
        Exception: Client initialization failure
    """
    prompt_print("Looking for a Trezor device ", end="", flush=True)
    animation = animate_dots(5)
    while True:
        try:
            client = get_safe_client()
            task = asyncio.get_event_loop().create_task(client_healthcheck(client))
            healthcheck_tasks.add(task)
            print()
            return client
        except TransportException:
            next(animation)  # Keep waiting
        except Exception:
            print()
            print("Unable to access a Trezor device")
            raise
        await asyncio.sleep(0.7)


async def client_healthcheck(client: TrezorClient):
    while True:
        try:
            await asyncio.get_event_loop().run_in_executor(None, client.ping, "healthcheck")
        except Exception as e:
            for task in asyncio.tasks.all_tasks():
                if not task.cancelled():
                    task.cancel("Trezor device has been disconnected")
            return
        await asyncio.sleep(1)