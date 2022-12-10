import json
from typing import List, Union
from urllib.parse import urlparse

from trezorlib.misc import decrypt_keyvalue
from trezorlib.tools import parse_path
from trezorlib.client import TrezorClient
from trezorlib.exceptions import TrezorException, TrezorFailure

from ..crypto import PATH, decrypt
from .tag import Tag


class Entry:
    def __init__(self, url: str) -> None:
        self.url = url
        self.title: str = None
        self.username: str = None
        self.nonce: str = None
        self.password: str = None
        self.safe_note: str = None
        self.tags: List[Tag] = None

        self._password_cleartext: str = None
        self._safe_note_cleartext: str = None

    @property
    def label(self) -> str:
        return self.note if self.note is not None else self.title

    @staticmethod
    def emptify(value: Union[str, None]) -> str:
        return value if value else "<empty>"

    @staticmethod
    def load(dict, tags: dict[str, Tag]):
        entry = Entry(dict["title"]) # title field in JSON is actually the url
        entry.__dict__.update(dict)
        entry.title = dict["note"] # and note field is the title
        entry.tags = [tags[key] for key in dict["tags"]]
        return entry

    def _get_entry_key(self, client: TrezorClient):
        address_n = parse_path(PATH)

        url = urlparse(self.url)
        if url.scheme in ('ftp', 'http', 'https'):
            domain = url.netloc
        else:
            domain = self.url
        key = f'Unlock {domain} for user {self.username}?'
        value = bytes.fromhex(self.nonce)
        try:
            return decrypt_keyvalue(client, address_n, key, value, ask_on_encrypt=False).hex()
        except TrezorException:
            raise
        except:
            raise TrezorFailure()

    def decrypt(self, client: TrezorClient):
        enc_key = self._get_entry_key(client)
        self._password_cleartext = json.loads(decrypt(enc_key, bytes(self.password["data"])).decode("utf8"))
        self._safe_note_cleartext = json.loads(decrypt(enc_key, bytes(self.safe_note["data"])).decode("utf8"))

    def password_cleartext(self, client: TrezorClient) -> str:
        if self._password_cleartext is None:
            self.decrypt(client)
        return self._password_cleartext

    def safe_note_cleartext(self, client: TrezorClient) -> str:
        if self._safe_note_cleartext is None:
            self.decrypt(client)
        return self._safe_note_cleartext
