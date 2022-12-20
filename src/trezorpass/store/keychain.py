from hmac import HMAC
from hashlib import sha256
from urllib.parse import urlparse

from trezorlib.client import TrezorClient
from trezorlib.exceptions import TrezorFailure
from trezorlib.misc import encrypt_keyvalue, decrypt_keyvalue
from trezorlib.tools import parse_path

from trezorpass.crypto import PATH, FILENAME_MESS
from trezorpass.store.containers import Entry


class Keychain:
    def __init__(self, client: TrezorClient):
        self.client = client

        address_n = parse_path(PATH)
        key = "Activate TREZOR Password Manager?"
        value = bytes.fromhex(
            "2d650551248d792eabf628f451200d7f51cb63e46aadcbb1038aacb05e8c8aee2d650551248d792eabf628f451200d7f51cb63e46aadcbb1038aacb05e8c8aee"
        )
        try:
            self.master_key = encrypt_keyvalue(client, address_n, key, value).hex()
        except Exception as e:
            raise TrezorFailure() from e

    @property
    def store_key(self) -> str:
        return self.master_key[len(self.master_key) // 2:]

    @property
    def store_name(self) -> str:
        file_key = self.master_key[:len(self.master_key) // 2]
        return HMAC(file_key.encode(), FILENAME_MESS.encode(), sha256).hexdigest() + '.pswd'

    def entry_key(self, entry: Entry) -> str:
        address_n = parse_path(PATH)
        url = urlparse(entry.url)
        if url.scheme in ('ftp', 'http', 'https'):
            domain = url.netloc
        else:
            domain = url
        key = f'Unlock {domain} for user {entry.username}?'
        value = bytes.fromhex(entry.nonce)
        try:
            return decrypt_keyvalue(self.client, address_n, key, value, ask_on_encrypt=False).hex()
        except Exception as e:
            raise TrezorFailure() from e
