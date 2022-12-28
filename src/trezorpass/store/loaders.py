from .keychain import Keychain
from .sources import Source
from .errors import StoreLoadError


class StoreLoader:
    def __init__(self, keychain: Keychain):
        self.keychain = keychain

    async def load(self, source: Source) -> bytes:
        try:
            return await source.load_store(self.keychain.store_name)
        except Exception as e:
            raise StoreLoadError() from e
