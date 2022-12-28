import json

from .tag import Tag
from .entry import EncryptedEntry
from .keychain import Keychain
from .store import Store
from .errors import StoreDecodeError


class EntryDecoder:
    def decode(self, entry_dict: dict) -> EncryptedEntry:
        return EncryptedEntry(
            url=entry_dict["title"],  # Intended
            title=entry_dict["note"],  # Intended
            username=entry_dict["username"],
            nonce=entry_dict["nonce"],
            encrypted_password=bytes(entry_dict["password"]["data"]),
            encrypted_safe_note=bytes(entry_dict["safe_note"]["data"]),
            tags=[]
        )


class TagDecoder:
    def decode(self, tag_dict: dict) -> Tag:
        return Tag(
            title=tag_dict["title"]
        )


class StoreDecoder:
    def __init__(self, keychain: Keychain, entry_decoder: EntryDecoder, tag_decoder: TagDecoder):
        self.keychain = keychain
        self.entry_decoder = entry_decoder
        self.tag_decoder = tag_decoder

    def decode(self, encoded_store: bytes) -> Store:
        try:
            store_dict = json.loads(encoded_store)
            tags_dict = store_dict['tags']
            entries_dict = store_dict['entries']
            tags = [self.tag_decoder.decode(tags_dict[key]) for key in tags_dict]
            entries = [self.entry_decoder.decode(entries_dict[key]) for key in entries_dict]
            return Store(
                name=self.keychain.store_name,
                entries=entries,
                tags=tags
            )
        except Exception as e:
            raise StoreDecodeError() from e
