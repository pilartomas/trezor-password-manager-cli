from typing import List

from .tag import Tag


class Entry:
    def __init__(self, *, url: str, title: str, username: str, nonce: str, tags: List[Tag]):
        self.url = url
        self.title = title
        self.username = username
        self.nonce = nonce
        self.tags: List[Tag] = tags


class EncryptedEntry(Entry):
    def __init__(self, *, encrypted_password: bytes, encrypted_safe_note: bytes, **kwargs):
        super().__init__(**kwargs)
        self.encrypted_password = encrypted_password
        self.encrypted_safe_note = encrypted_safe_note


class DecryptedEntry(Entry):
    def __init__(self, *, password: str, safe_note: str, **kwargs):
        super().__init__(**kwargs)
        self.password = password
        self.safe_note = safe_note
