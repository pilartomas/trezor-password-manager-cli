import json

from trezorpass.crypto import decrypt
from trezorpass.store.containers import EncryptedEntry, DecryptedEntry
from trezorpass.store.keychain import Keychain


class EntryDecoder:
    def decode(self, entry_dict) -> EncryptedEntry:
        return EncryptedEntry(
            url=entry_dict["title"],  # Intended
            title=entry_dict["note"],  # Intended
            username=entry_dict["username"],
            nonce=entry_dict["nonce"],
            encrypted_password=entry_dict["password"]["data"],
            encrypted_safe_note=entry_dict["safe_note"]["data"],
            tags=[]
        )


class EntryDecrypter:
    def __init__(self, keychain: Keychain):
        self.keychain = keychain

    def decrypt(self, entry: EncryptedEntry) -> DecryptedEntry:
        key = self.keychain.entry_key(entry)
        password = json.loads(decrypt(key, bytes(entry.encrypted_password)).decode("utf8"))
        safe_note = json.loads(decrypt(key, bytes(entry.encrypted_safe_note)).decode("utf8"))
        return DecryptedEntry(
            url=entry.url,
            title=entry.title,
            username=entry.username,
            nonce=entry.nonce,
            tags=entry.tags,
            password=password,
            safe_note=safe_note
        )
