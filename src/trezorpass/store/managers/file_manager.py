from .manager import Manager

class FileManager(Manager):
    def __init__(self, filename: str) -> None:
        self.filename = filename

    async def load_store(self, store_name) -> bytes:
        with open(self.filename, "rb") as file:
            return file.read()