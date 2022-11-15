from .source import Source

class FileSource(Source):
    def __init__(self, filename: str | None) -> None:
        self.filename = filename

    async def load_store(self, store_name) -> bytes:
        filename = self.filename if self.filename else store_name
        with open(filename, "rb") as file:
            return file.read()