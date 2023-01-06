from dataclasses import dataclass

from .tag import Tag


@dataclass(kw_only=True)
class Entry:
    url: str
    title: str
    username: str
    nonce: str
    tags: list[Tag]


@dataclass(kw_only=True)
class EncryptedEntry(Entry):
    encrypted_password: bytes
    encrypted_safe_note: bytes


@dataclass(kw_only=True)
class DecryptedEntry(Entry):
    password: str
    safe_note: str
