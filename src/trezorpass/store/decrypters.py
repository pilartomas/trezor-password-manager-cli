import json

from ..crypto import decrypt
from .keychain import Keychain
from .entry import EncryptedEntry, DecryptedEntry
from .errors import StoreDecryptError


class EntryDecrypter:
    def __init__(self, keychain: Keychain):
        self.keychain = keychain

    def decrypt(self, entry: EncryptedEntry) -> DecryptedEntry:
        key = self.keychain.entry_key(entry)
        password = json.loads(decrypt(key, entry.encrypted_password).decode("utf8"))
        safe_note = json.loads(decrypt(key, entry.encrypted_safe_note).decode("utf8"))
        return DecryptedEntry(
            url=entry.url,
            title=entry.title,
            username=entry.username,
            nonce=entry.nonce,
            tags=entry.tags,
            password=password,
            safe_note=safe_note
        )


class StoreDecrypter:
    def __init__(self, keychain: Keychain):
        self.keychain = keychain

    def decrypt(self, encrypted_store: bytes) -> bytes:
        try:
            return decrypt(self.keychain.store_key, encrypted_store)
        except Exception as e:
            raise StoreDecryptError() from e
