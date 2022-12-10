from typing import List, Tuple
import json
from hmac import HMAC
from hashlib import sha256

from trezorlib.misc import encrypt_keyvalue
from trezorlib.tools import parse_path
from trezorlib.client import TrezorClient
from trezorlib.exceptions import TrezorException, TrezorFailure

from ..crypto import PATH, FILENAME_MESS, decrypt
from .entry import Entry
from .sources import Source
from .tag import Tag


class Store:
    def __init__(self, client: TrezorClient, source: Source):
        self.client = client
        self.entries: List[Entry] = []
        self.tags: List[Tag] = []
        self._master_key = self._load_master_key(client)
        self.source = source

    async def load(self) -> None:
        """Loads the store content from the source

        Raises:
            StoreLoadError
            StoreDecryptError
            StoreDecodeError
        """
        encrypted_store = await self._load_encrypted_store()
        encoded_store = self._decrypt_store(encrypted_store)
        (tags, entries) = self._decode_store(encoded_store)
        self.tags = tags
        self.entries = entries

    async def __aenter__(self):
        await self.load()
        return self

    async def __aexit__(self, *args):
        pass

    @staticmethod
    def _load_master_key(client: TrezorClient) -> str:
        address_n = parse_path(PATH)
        key = "Activate TREZOR Password Manager?"
        value = bytes.fromhex(
            "2d650551248d792eabf628f451200d7f51cb63e46aadcbb1038aacb05e8c8aee2d650551248d792eabf628f451200d7f51cb63e46aadcbb1038aacb05e8c8aee")
        try:
            return encrypt_keyvalue(client, address_n, key, value).hex()
        except TrezorException:
            raise
        except:
            raise TrezorFailure()

    @property
    def name(self) -> str:
        file_key = self._master_key[:len(self._master_key) // 2]
        return HMAC(file_key.encode(), FILENAME_MESS.encode(), sha256).hexdigest() + '.pswd'

    async def _load_encrypted_store(self) -> bytes:
        try:
            return await self.source.load_store(self.name)
        except Exception as e:
            raise StoreLoadError() from e

    def _decrypt_store(self, encrypted_store: bytes) -> bytes:
        """Returns JSON representation of the password store"""
        enc_key = self._master_key[len(self._master_key) // 2:]
        try:
            return decrypt(enc_key, encrypted_store)
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


class StoreLoadError(Exception):
    pass


class StoreDecryptError(Exception):
    pass


class StoreDecodeError(Exception):
    pass
