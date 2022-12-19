from typing import List, Tuple
import json
from hmac import HMAC
from hashlib import sha256

from trezorlib.misc import encrypt_keyvalue
from trezorlib.tools import parse_path
from trezorlib.client import TrezorClient
from trezorlib.exceptions import TrezorFailure

from trezorpass.crypto import PATH, FILENAME_MESS, decrypt
from trezorpass.store import Entry, Tag
from trezorpass.store.sources import Source


class Store:
    def __init__(self, name: str, entries: List[Entry], tags: List[Tag]):
        self.name = name
        self.entries = entries
        self.tags = tags


class StoreLoader:
    def __init__(self, source: Source):
        self.source = source

    async def load(self, *, name: str, key: str) -> Store:
        """Loads the store content from the source

        Raises:
            StoreLoadError
            StoreDecryptError
            StoreDecodeError
        """
        encrypted_store = await self._load_encrypted_store(name)
        encoded_store = self._decrypt_store(key, encrypted_store)
        (tags, entries) = self._decode_store(encoded_store)
        return Store(name, entries, tags)

    async def _load_encrypted_store(self, name: str) -> bytes:
        try:
            return await self.source.load_store(name)
        except Exception as e:
            raise StoreLoadError() from e

    @staticmethod
    def _decrypt_store(key: str, encrypted_store: bytes) -> bytes:
        """Returns JSON representation of the password store"""
        try:
            return decrypt(key, encrypted_store)
        except Exception as e:
            raise StoreDecryptError() from e

    @staticmethod
    def _decode_store(json_store: bytes) -> Tuple[List[Tag], List[Entry]]:
        """Returns object representation of the password store"""
        try:
            dict = json.loads(json_store)
            raw_tags = {int(key): Tag.load(dict['tags'][key]) for key in dict['tags']}
            tags = [raw_tags[key] for key in raw_tags]
            entries = [Entry.load(dict['entries'][key], raw_tags) for key in dict['entries']]
            return [tags, entries]
        except Exception as e:
            raise StoreDecodeError() from e


class StoreSaver:
    def __init__(self, source: Source):
        self.source = source

    async def store(self, *, key: str, store: Store):
        pass


class StoreManager:
    def __init__(self, *, client: TrezorClient, loader: StoreLoader, saver: StoreSaver):
        self.client = client
        self.loader = loader
        self.saver = saver

    async def __aenter__(self):
        master_key = self._obtain_master_key()
        self.encryption_key = master_key[len(master_key) // 2:]
        self.store = await self.loader.load(name=self.derive_name(master_key), key=self.encryption_key)
        return self.store

    async def __aexit__(self, *args):
        await self.saver.store(key=self.encryption_key, store=self.store)

    def _obtain_master_key(self) -> str:
        address_n = parse_path(PATH)
        key = "Activate TREZOR Password Manager?"
        value = bytes.fromhex(
            "2d650551248d792eabf628f451200d7f51cb63e46aadcbb1038aacb05e8c8aee2d650551248d792eabf628f451200d7f51cb63e46aadcbb1038aacb05e8c8aee"
        )
        try:
            return encrypt_keyvalue(self.client, address_n, key, value).hex()
        except Exception as e:
            raise TrezorFailure() from e

    @staticmethod
    def derive_name(master_key: str) -> str:
        file_key = master_key[:len(master_key) // 2]
        return HMAC(file_key.encode(), FILENAME_MESS.encode(), sha256).hexdigest() + '.pswd'


class StoreLoadError(Exception):
    pass


class StoreDecryptError(Exception):
    pass


class StoreDecodeError(Exception):
    pass
