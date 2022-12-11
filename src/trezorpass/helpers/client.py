import asyncio

from trezorlib.client import TrezorClient
from trezorlib.transport import TransportException

from ..client import get_default_client
from ..utils import animate_dots, prompt_print


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
            client = get_default_client()
            print()
            return client
        except TransportException:
            next(animation)  # Keep waiting
        except Exception:
            print()
            print("Unable to access a Trezor device")
            raise
        await asyncio.sleep(0.7)
