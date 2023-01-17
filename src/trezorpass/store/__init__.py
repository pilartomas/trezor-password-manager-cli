from contextlib import asynccontextmanager

from .entry import *
from .store import *
from .tag import *
from .loaders import *
from .decoders import *
from .decrypters import *


@asynccontextmanager
async def get_default_store_manager(keychain: Keychain, source: Source):
    loader = StoreLoader(keychain)
    decrypter = StoreDecrypter(keychain)
    decoder = StoreDecoder(keychain, EntryDecoder(), TagDecoder())

    loaded_store = await loader.load(source)
    decrypted_store = decrypter.decrypt(loaded_store)
    yield decoder.decode(decrypted_store)
