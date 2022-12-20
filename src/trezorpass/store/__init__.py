from trezorpass.store.containers import *
from trezorpass.store.entry import *
from trezorpass.store.store import *
from trezorpass.store.tag import *


def get_store_manager(keychain: Keychain, source: Source) -> StoreManager:
    return StoreManager(
        source,
        loader=StoreLoader(keychain),
        decrypter=StoreDecrypter(keychain),
        decoder=StoreDecoder(keychain, EntryDecoder(), TagDecoder())
    )
