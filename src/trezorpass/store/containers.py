from typing import List


class Tag:
    def __init__(self, *, title: str) -> None:
        self.title = title


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


class Store:
    def __init__(self, name: str, entries: List[Entry], tags: List[Tag]):
        self.name = name
        self.entries = entries
        self.tags = tags
