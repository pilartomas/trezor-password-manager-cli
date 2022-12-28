from typing import List

from .entry import EncryptedEntry
from .tag import Tag


class Store:
    def __init__(self, *, name: str, entries: List[EncryptedEntry], tags: List[Tag]):
        self.name = name
        self.entries = entries
        self.tags = tags
