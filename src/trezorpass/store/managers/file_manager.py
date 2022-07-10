from InquirerPy import inquirer
from InquirerPy.validator import PathValidator

from .manager import Manager

class FileManager(Manager):
    @property
    async def password_store(self) -> bytes:
        filepath = await inquirer.filepath(
            "Enter path to the password store file:",
            validate=PathValidator(is_file=True, message="Input is not a file")
        ).execute_async()
        with open(filepath, "rb") as file:
            return file.read()