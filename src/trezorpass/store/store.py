from __future__ import annotations
from typing import Callable, List
import json
from hmac import HMAC
from hashlib import sha256

from trezorlib.misc import encrypt_keyvalue
from trezorlib.tools import parse_path
from trezorlib.client import TrezorClient
from trezorlib.transport import TransportException
from InquirerPy import inquirer
from InquirerPy.base.control import Choice

from trezorpass.utils import PROMPT, prompt_trezor

from ..crypto import PATH, FILENAME_MESS, decrypt
from ..entry import Entry
from .managers import Manager, DropboxManager, FileManager
from .store_location import StoreLocation
from ..tag import Tag

class Store:
    def __init__(self, client: TrezorClient, manager_factory: Callable[[Store], Manager]):
        self.client = client
        self.entries: List[Entry] = []
        self.tags: List[Tag] = []
        self._lazy_master_key = None
        self._manager = manager_factory(self)

    @property
    def _master_key(self) -> str:
        if not self._lazy_master_key:
            self._lazy_master_key = self._get_master_key(self.client)
        return self._lazy_master_key

    @staticmethod
    def _get_master_key(client: TrezorClient) -> str:
        address_n = parse_path(PATH)
        key = "Activate TREZOR Password Manager?"
        value = bytes.fromhex("2d650551248d792eabf628f451200d7f51cb63e46aadcbb1038aacb05e8c8aee2d650551248d792eabf628f451200d7f51cb63e46aadcbb1038aacb05e8c8aee")
        prompt_trezor()
        return encrypt_keyvalue(client, address_n, key, value).hex()

    @property
    def filename(self) -> str:
        file_key = self._master_key[:len(self._master_key) // 2]
        return HMAC(file_key.encode(), FILENAME_MESS.encode(), sha256).hexdigest() + '.pswd'

    @staticmethod
    def _decrypt_store(encryptedStore: bytes, store: Store) -> str:
        '''Returns JSON representation of the password store'''
        enc_key = store._master_key[len(store._master_key) // 2:]
        try:
            return decrypt(enc_key, encryptedStore).decode('utf8')
        except:
            raise StoreDecryptError()

    @staticmethod
    def _decode_store(json_store: str, store: Store) -> Store:
        '''Returns object representation of the password store'''
        try:
            dict = json.loads(json_store)
            tags = {int(key): Tag.load(dict['tags'][key]) for key in dict['tags']}
            store.tags = [tags[key] for key in tags]
            store.entries = [Entry.load(dict['entries'][key], tags) for key in dict['entries']]
            return store
        except:
            raise StoreDecodeError()

    @staticmethod
    def load(client: TrezorClient) -> Store:
        location = inquirer.select("Where is the password store located at?", choices=[
            Choice(StoreLocation.Dropbox, "Dropbox"),
            Choice(StoreLocation.Filepath, "Filepath"),
        ], qmark=PROMPT, amark=PROMPT).execute()
        if location == StoreLocation.Dropbox:
            store = Store(client, lambda store: DropboxManager(store.filename))
        elif location == StoreLocation.Filepath:
            store = Store(client, lambda store: FileManager())
        else:
            raise Exception("Unreachable code")

        json_store = Store._decrypt_store(store._manager.password_store, store)
        return Store._decode_store(json_store, store)

class StoreDecryptError(Exception):
    pass

class StoreDecodeError(Exception):
    pass