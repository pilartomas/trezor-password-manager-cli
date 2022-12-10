from trezorlib.client import TrezorClient

from ..store.sources import Source
from ..store import Store


async def load_store(client: TrezorClient, source: Source) -> Store:
    """Loads the password store using the specified Trezor client and store source

    Returns:
        Password store instance

    Raises:
        StoreDecryptError
        StoreDecodeError
        KeyboardInterrupt
        Exception
    """
    try:
        store = Store(client, source)
        await store.load()
        return store
    except Exception:
        print("Unable to load the password store")
        raise