from dataclasses import dataclass, field

from .entry import EncryptedEntry
from .tag import Tag


@dataclass(kw_only=True)
class Store:
    name: str
    entries: list[EncryptedEntry] = field(default_factory=list)
    tags: list[Tag] = field(default_factory=list)

