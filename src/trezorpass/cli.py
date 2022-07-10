from typing import List
import time
import sys

from trezorlib.client import get_default_client, TrezorClient
from trezorlib.transport import TransportException
from trezorlib.exceptions import Cancelled, PinException, TrezorFailure

from InquirerPy import inquirer

from pyperclip import copy

from trezorpass.entry import Entry
from trezorpass.store import Store
from trezorpass.store.store import StoreDecodeError, StoreDecryptError
from trezorpass.utils import animate_dots, welcome, goodbye

def select_entry(entries: List[Entry], long_instruction: str) -> Entry:
    '''Selects an entry'''
    choices = [{"value": entry, "name":entry.note if entry.note is not None else entry.title} for entry in entries]
    selection = inquirer.fuzzy(
        message="Select an entry:",
        choices=choices,
        long_instruction=long_instruction
    ).execute()
    return selection

def get_client() -> TrezorClient:
    '''Gets the Trezor client'''
    print("Looking for a Trezor device ", end="", flush=True)
    animation = animate_dots(5)
    while True:
        try:
            client = get_default_client()
            print()
            print("Device ready")
            return client
        except TransportException:
            next(animation)
        except KeyboardInterrupt:
            print()
            raise
        except:
            print()
            print("Unable to access a Trezor device")
            raise
        time.sleep(0.7)

def load_store(client: TrezorClient) -> Store:
    while True:
        try:
            return Store.load(client)
        except StoreDecryptError:
            print("Unable to decrypt the password store")
        except StoreDecodeError:
            print("Unable to decode the password store")
        except KeyboardInterrupt:
            raise
        except:
            print("Unable to load the password store")

def manage_entry(entry: Entry, client: TrezorClient) -> None:
    try:
        long_instruction = "Press Ctrl+C to leave the entry"
        while True:
            action = inquirer.select("Select an action:", ['Show entry', 'Copy to clipboard', 'Show entry including secrets'], long_instruction=long_instruction).execute()
            if action == "Show entry":
                print(entry.show(client))
            elif action == "Copy to clipboard":
                key = inquirer.select("Select the value to copy:", ['username', 'password'], long_instruction=long_instruction).execute()
                if key == 'username':
                    copy(entry.username)
                elif key == 'password':
                    copy(entry.password_cleartext(client))
                print(f"{key} has been copied to the clipboard")
            elif action == "Show entry including secrets":
                print(entry.show(client, secrets=True))
    except KeyboardInterrupt:
        pass

def cli():
    welcome()
    try:
        client = None
        store = None
        entry = None
        while True:
            try:
                if not client:
                    client = get_client()
                    if store:
                        store.client = client
                if not store:
                    store = load_store(client)
                if not entry:
                    entry = select_entry(store.entries, long_instruction="Press Ctrl+C to exit")
                manage_entry(entry, client)
                entry = None
            except TrezorFailure:
                client = None
                print("Connection to the Trezor device has been lost")
            except Cancelled:
                print("Trezor operation has been cancelled")
            except PinException:
                print("Invalid pin")
    except KeyboardInterrupt:
        pass
    except:
        print("Unexpected error")
        exit(1)
    finally:
        goodbye()

if __name__ == "__main__":
    cli()