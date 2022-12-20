import json
from typing import List

from trezorpass.crypto import decrypt
from trezorpass.store.keychain import Keychain
from trezorpass.store.tag import Tag


class Entry:
    def __init__(self, *, url: str, title: str, username: str, nonce: str, tags: List[Tag]):
        self.url = url
        self.title = title
        self.username = username
        self.nonce = nonce
        self.tags: List[Tag] = tags

    @property
    def label(self) -> str:
        return self.note if self.note is not None else self.title


class EncryptedEntry(Entry):
    def __init__(self, *, encrypted_password: str, encrypted_safe_note: str, **kwargs):
        super().__init__(**kwargs)
        self.encrypted_password = encrypted_password
        self.encrypted_safe_note = encrypted_safe_note


class DecryptedEntry(Entry):
    def __init__(self, *, password: str, safe_note: str, **kwargs):
        super().__init__(**kwargs)
        self.password = password
        self.safe_note = safe_note


class EntryDecoder:
    def decode(self, entry_dict) -> EncryptedEntry:
        return EncryptedEntry(
            url=entry_dict["title"],  # Intended
            title=entry_dict["note"],  # Intended
            username=entry_dict["username"],
            nonce=entry_dict["nonce"],
            encrypted_password=entry_dict["password"]["data"],
            encrypted_safe_note=entry_dict["password"]["data"],
            tags=[]
        )


class EntryDecrypter:
    def __init__(self, keychain: Keychain):
        self.keychain = keychain

    def decrypt(self, entry: EncryptedEntry) -> DecryptedEntry:
        key = self.keychain(entry)
        password = json.loads(decrypt(key, bytes(entry.encrypted_password)).decode("utf8"))
        secret_note = json.loads(decrypt(key, bytes(entry.encrypted_safe_note)).decode("utf8"))
        return DecryptedEntry(
            url=entry.url,
            title=entry.title,
            username=entry.username,
            nonce=entry.nonce,
            tags=entry.tags,
            password=password,
            secret_note=secret_note
        )
