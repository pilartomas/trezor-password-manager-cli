from trezorpass.store.containers import Tag


class TagDecoder:
    def decode(self, tag_dict) -> Tag:
        return Tag(
            title=tag_dict["title"]
        )
