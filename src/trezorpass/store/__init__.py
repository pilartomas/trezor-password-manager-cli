from .entry import *
from .store import *
from .tag import *
from .loaders import *
from .decoders import *
from .decrypters import *


class StoreManager:
    def __init__(self, source: Source, *, loader: StoreLoader, decrypter: StoreDecrypter, decoder: StoreDecoder):
        self.source = source
        self.loader = loader
        self.decrypter = decrypter
        self.decoder = decoder

    async def __aenter__(self):
        loaded_store = await self.loader.load(self.source)
        decrypted_store = self.decrypter.decrypt(loaded_store)
        self.store = self.decoder.decode(decrypted_store)
        return self.store

    async def __aexit__(self, *args):
        pass


def get_store_manager(keychain: Keychain, source: Source) -> StoreManager:
    return StoreManager(
        source,
        loader=StoreLoader(keychain),
        decrypter=StoreDecrypter(keychain),
        decoder=StoreDecoder(keychain, EntryDecoder(), TagDecoder())
    )
