from typing import List

from trezorlib.client import get_default_client
from trezorlib.transport import TransportException

from InquirerPy import inquirer

from trezorpass.entry import Entry
from trezorpass.store import Store

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
    client = None
    while not client:
        try:
            client = get_default_client()
        except TransportException as ex:
            retry = inquirer.confirm("No available Trezor device, please plug it in and retry. Proceed?", default=True, amark="#").execute()
            if not retry:
                exit(1)

    store = None
    while not store:
        try:
            store = Store.load(client)
        except Exception as ex:
            retry = inquirer.confirm("Failed to load the password store, please retry. Proceed?", default=True, amark="#").execute()
            if not retry:
                exit(1)

    while True:
        try:
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
            break

if __name__ == "__main__":
    cli()