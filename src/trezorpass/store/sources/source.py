class Source:
    async def load_store(self, store_name: str) -> bytes:
        raise NotImplementedError()

class SourceError(Exception):
    pass