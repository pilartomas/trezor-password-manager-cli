from typing import List

from trezorlib.client import get_default_client, TrezorClient
from trezorlib.transport import TransportException
from trezorlib.exceptions import Cancelled, PinException, TrezorFailure

from InquirerPy import inquirer

from pyperclip import copy

from trezorpass.entry import Entry
from trezorpass.store import Store
from trezorpass.store.store import StoreDecodeError, StoreDecryptError
from trezorpass.utils import PROMPT, prompt_print, welcome, goodbye

def select_entry(entries: List[Entry]) -> Entry:
    '''Selects an entry'''
    choices = [{"value": entry, "name":entry.note if entry.note is not None else entry.title} for entry in entries]
    selection = inquirer.fuzzy(
        message="Select an entry:",
        choices=choices,
        qmark=PROMPT,
        amark=PROMPT
    ).execute()
    return selection

def get_client() -> TrezorClient:
    '''Gets the Trezor client or gracefully exits the CLI'''
    while True:
        try:
            client = get_default_client()
            prompt_print("Device ready")
            return client
        except TransportException as ex:
            prompt_print("No available Trezor device")
        except:
            prompt_print("Unable to access a Trezor device")
        retry = inquirer.confirm("Retry?", long_instruction="Make sure your Trezor device is connected before proceeding", qmark=PROMPT, amark=PROMPT, default=True, mandatory=False).execute()
        if retry is False:
            goodbye()
            exit(1)

def load_store(client: TrezorClient) -> Store:
    '''Loads the password store or gracefully exits the CLI'''
    while True:
        try:
            return Store.load(client)
        except Cancelled:
            prompt_print("Trezor operation has been cancelled")
        except PinException:
            prompt_print("Invalid pin")
        except StoreDecryptError:
            prompt_print("Unable to decrypt the password store")
        except StoreDecodeError:
            prompt_print("Unable to decode the password store")
        except:
            prompt_print("Unable to load the password store")
        retry = inquirer.confirm("Retry?", default=True, qmark=PROMPT, amark=PROMPT).execute()
        if retry is False:
            goodbye()
            exit(1)

def read_entry(entry: Entry, client: TrezorClient) -> None:
    entry_prompt = PROMPT + "#" + entry.title
    prompt_print("Press Ctrl+c to leave the entry", entry_prompt)
    while True:
        action = inquirer.select("Select an action:", ['Show entry', 'Copy to clipboard', 'Show entry including secrets'], qmark=entry_prompt, amark=entry_prompt).execute()
        if action == "Show entry":
            print(entry.show(client))
        elif action == "Copy to clipboard":
            key = inquirer.select("Select the value to copy:", ['username', 'password'], qmark=entry_prompt, amark=entry_prompt).execute()
            if key == 'username':
                copy(entry.username)
            elif key == 'password':
                copy(entry.password_cleartext(client))
            prompt_print(f"{key} has been copied to the clipboard")
        elif action == "Show entry including secrets":
            print(entry.show(client, secrets=True))

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
                    entry = select_entry(store.entries)
                try:
                    read_entry(entry, client)
                except KeyboardInterrupt:
                    entry = None
                loop = inquirer.confirm(message="Choose another entry?", default=True, qmark=PROMPT, amark=PROMPT).execute()
                if not loop:
                    break
            except TrezorFailure:
                client = None
                prompt_print("Connection to the Trezor device has been lost")
            except Cancelled:
                prompt_print("Trezor operation has been cancelled")
            except PinException:
                prompt_print("Invalid pin")
            retry = inquirer.confirm("Retry?", default=True, qmark=PROMPT, amark=PROMPT).execute()
            if retry is False:
                goodbye()
                exit(1)
    except KeyboardInterrupt:
        pass
    except:
        prompt_print("Unexpected error")
        exit(1)
    goodbye()

if __name__ == "__main__":
    cli()