from turtle import color
from typing import List

from trezorlib.client import get_default_client
from trezorlib.transport import TransportException

from InquirerPy import inquirer

from trezorpass.entry import Entry
from trezorpass.store import Store
from trezorpass.utils import PROMPT, prompt_print, welcome, goodbye

def select_entry(entries: List[Entry]) -> Entry:
    '''Lets the user select an entry'''

    choices = [{"value": entry, "name":entry.note if entry.note is not None else entry.title} for entry in entries]
    selection = inquirer.fuzzy(
        message="Select an entry:",
        choices=choices,
    ).execute()
    return selection

def print_trezor():
    print("Proceed on your Trezor device")

def cli():
    welcome()

    try:
        client = None
        while not client:
            try:
                client = get_default_client()
                prompt_print("Device ready")
            except TransportException as ex:
                prompt_print("No available Trezor device")
                retry = inquirer.confirm("Retry?", long_instruction="Make sure your Trezor device is connected before proceeding", qmark=PROMPT, amark=PROMPT, default=True, mandatory=False).execute()
                if retry is False:
                    exit(1)

        store = None
        while not store:
            try:
                store = Store.load(client)
            except Exception as ex:
                retry = inquirer.confirm("Failed to load the password store, please retry. Retry?", default=True, qmark=PROMPT, amark=PROMPT, mandatory=False).execute()
                if retry is False:
                    exit(1)

        while True:
                selected_entry = select_entry(store.entries)
                print(selected_entry)

                if not selected_entry.decrypted:
                    decrypt = inquirer.confirm(message="Decrypt entry?", default=False).execute()
                    if decrypt:
                        try:
                            print_trezor()
                            selected_entry.decrypt(client)
                            print(selected_entry)
                        except:
                            print("Decryption Failed")

                loop = inquirer.confirm(message="Choose another entry?", default=False).execute()
                if not loop:
                    break
    except KeyboardInterrupt:
        pass

    goodbye()

if __name__ == "__main__":
    cli()