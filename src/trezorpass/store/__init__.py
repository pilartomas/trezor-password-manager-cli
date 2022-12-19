from trezorpass.store.entry import *
from trezorpass.store.store import *
from trezorpass.store.tag import *


def get_store_manager(client: TrezorClient, source: Source) -> StoreManager:
    return StoreManager(
        client=client,
        loader=StoreLoader(source),
        saver=StoreSaver(source)
    )
