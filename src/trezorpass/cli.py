from turtle import color
from typing import List

from trezorlib.client import get_default_client, TrezorClient
from trezorlib.transport import TransportException
from trezorlib.exceptions import Cancelled, PinException
from libusb1 import USBError

from InquirerPy import inquirer

from trezorpass.entry import Entry
from trezorpass.store import Store
from trezorpass.store.store import StoreDecodeError, StoreDecryptError
from trezorpass.utils import PROMPT, prompt_print, welcome, goodbye

def select_entry(entries: List[Entry]) -> Entry:
    '''Lets the user select an entry'''

    choices = [{"value": entry, "name":entry.note if entry.note is not None else entry.title} for entry in entries]
    selection = inquirer.fuzzy(
        message="Select an entry:",
        choices=choices,
        qmark=PROMPT,
        amark=PROMPT
    ).execute()
    return selection

def get_client() -> TrezorClient:
    client = None
    while not client:
        try:
            client = get_default_client()
            prompt_print("Device ready")
        except TransportException as ex:
            prompt_print("No available Trezor device")
            retry = inquirer.confirm("Retry?", long_instruction="Make sure your Trezor device is connected before proceeding", qmark=PROMPT, amark=PROMPT, default=True, mandatory=False).execute()
            if retry is False:
                goodbye()
                exit(1)
    return client

def get_store(client: TrezorClient) -> Store:
    while True:
        try:
            return Store.load(client)
        except Cancelled:
            prompt_print("Trezor operation has been cancelled")
        except PinException:
            prompt_print("Invalid pin")
        except StoreDecryptError:
            prompt_print("Unable to decrypt password store")
        except StoreDecodeError:
            prompt_print("Unable to decode password store")
        retry = inquirer.confirm("Retry?", default=True, qmark=PROMPT, amark=PROMPT).execute()
        if retry is False:
            goodbye()
            exit(1)

def cli():
    welcome()
    try:
        client = None
        store = None
        while True:
            if not client:
                client = get_client()
                if store:
                    store.client = client
            try:
                if not store:
                    store = get_store(client)
                selected_entry = select_entry(store.entries)
                print(selected_entry)
                if not selected_entry.decrypted:
                    decrypt = inquirer.confirm(message="Decrypt the entry?", default=False, qmark=PROMPT, amark=PROMPT).execute()
                    if decrypt:
                        try:
                            selected_entry.decrypt(client)
                            print(selected_entry)
                        except:
                            prompt_print("Unable to decrypt the entry")
                loop = inquirer.confirm(message="Choose another entry?", default=True, qmark=PROMPT, amark=PROMPT).execute()
                if not loop:
                    break
            except USBError:
                client = None
                prompt_print("Connection to the Trezor device has been lost")
    except KeyboardInterrupt:
        pass
    goodbye()

if __name__ == "__main__":
    cli()