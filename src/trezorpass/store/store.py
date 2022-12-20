import json

from trezorpass.crypto import decrypt
from trezorpass.store.entry import EntryDecoder
from trezorpass.store.tag import TagDecoder
from trezorpass.store.containers import Store
from trezorpass.store.keychain import Keychain
from trezorpass.store.sources import Source


class StoreLoader:
    def __init__(self, keychain: Keychain):
        self.keychain = keychain

    async def load(self, source: Source) -> bytes:
        try:
            return await source.load_store(self.keychain.store_name)
        except Exception as e:
            raise StoreLoadError() from e


class StoreDecrypter:
    def __init__(self, keychain: Keychain):
        self.keychain = keychain

    def decrypt(self, encrypted_store: bytes) -> bytes:
        try:
            return decrypt(self.keychain.store_key, encrypted_store)
        except Exception as e:
            raise StoreDecryptError() from e


class StoreDecoder:
    def __init__(self, keychain: Keychain, entry_decoder: EntryDecoder, tag_decoder: TagDecoder):
        self.keychain = keychain
        self.entry_decoder = entry_decoder
        self.tag_decoder = tag_decoder

    def decode(self, encoded_store: bytes) -> Store:
        try:
            store_dict = json.loads(encoded_store)
            tags_dict = store_dict['tags']
            entries_dict = store_dict['entries']
            tags = [self.tag_decoder.decode(tags_dict[key]) for key in tags_dict]
            entries = [self.entry_decoder.decode(entries_dict[key]) for key in entries_dict]
            return Store(self.keychain.store_name, entries, tags)
        except Exception as e:
            raise StoreDecodeError() from e


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


class StoreLoadError(Exception):
    pass


class StoreDecryptError(Exception):
    pass


class StoreDecodeError(Exception):
    pass
