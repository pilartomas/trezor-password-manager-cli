class Source:
    """Loads the password store
    
    Args:
        store_name: Name of the store to load, implementors may ignore this argument
    """
    async def load_store(self, store_name: str | None) -> bytes:
        raise NotImplementedError()

class SourceError(Exception):
    pass