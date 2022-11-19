from typing import List
import asyncio
import webbrowser
import logging

from trezorlib.client import TrezorClient
from trezorlib.transport import TransportException
from trezorlib.exceptions import Cancelled, PinException
from InquirerPy import inquirer
from pyperclip import copy

from trezorpass.client import get_safe_client
from trezorpass.entry import Entry
from trezorpass.store.managers import Source, DropboxSource, FileSource
from trezorpass.store import Store
from trezorpass.utils import animate_dots, welcome, goodbye
from trezorpass.appdata import clear_data


async def select_entry(entries: List[Entry]) -> Entry:
    """Facilitates user interaction to select an entry from the given list of entries

    Returns:
        A single entry from the specified list of entries

    Raises:
        KeyboardInterrupt
    """
    choices = [{"value": entry, "name": entry.label} for entry in entries]
    selection = await inquirer.fuzzy(
        message="Select an entry:",
        choices=choices,
        long_instruction="Press Ctrl+C to exit"
    ).execute_async()
    return selection


healthcheck_tasks = set()


async def get_client() -> TrezorClient:
    """Waits for the Trezor client to connect

    Returns:
        The connected Trezor client

    Raises:
        KeyboardInterrupt
        Exception: Client initialization failure
    """
    print("Looking for a Trezor device ", end="", flush=True)
    animation = animate_dots(5)
    while True:
        try:
            client = get_safe_client()
            task = asyncio.get_event_loop().create_task(client_healthcheck(client))
            healthcheck_tasks.add(task)
            print()
            print("Trezor device ready")
            return client
        except TransportException:
            next(animation)  # Keep waiting
        except Exception:
            print()
            print("Unable to access a Trezor device")
            raise
        await asyncio.sleep(0.7)


async def load_store(client: TrezorClient, source: Source) -> Store:
    """Loads the password store using the specified Trezor client and store source

    Returns:
        Password store instance

    Raises:
        StoreDecryptError
        StoreDecodeError
        KeyboardInterrupt
        Exception
    """
    try:
        store = Store(client, source)
        await store.load()
        return store
    except Exception:
        print("Unable to load the password store")
        raise


async def manage_entry(entry: Entry, client: TrezorClient) -> None:
    """Facilitates interaction with the given entry"""
    clipboard_dirty = False
    try:
        while True:
            choices = [f'Open {entry.url}', 'Copy username to clipboard',
                       'Copy password to clipboard', 'Show entry',
                       'Show entry including secrets']
            action = await inquirer.select("Select an action:", choices=choices, long_instruction="Press Ctrl+C to "
                                                                                                  "leave the "
                                                                                                  "entry").execute_async()
            if action == choices[0]:
                webbrowser.open(entry.url, 2)
            elif action == choices[1]:
                copy(entry.username)
                print("Username has been copied to the clipboard")
            elif action == choices[2]:
                clipboard_dirty = True
                copy(entry.password_cleartext(client))
                print("Password has been copied to the clipboard")
            elif action == choices[3]:
                print(entry.show(client))
            elif action == choices[4]:
                print(entry.show(client, secrets=True))
    except KeyboardInterrupt:
        pass
    finally:
        if clipboard_dirty:
            print("Cleaning up the clipboard")
            copy("")


async def cli(store_manager: Source):
    welcome()
    client = None
    try:
        client = await get_client()
        store = await load_store(client, store_manager)
        while True:
            try:
                entry = await select_entry(store.entries)
                await manage_entry(entry, client)
            except Cancelled:
                print("Trezor operation has been cancelled")
            except PinException:
                print("Invalid pin")
    except KeyboardInterrupt:
        pass
    except Exception:
        logging.exception("CLI failed")
    finally:
        if client:
            try:
                client.end_session()
            except:
                pass
        goodbye()


async def client_healthcheck(client: TrezorClient):
    while True:
        try:
            await asyncio.get_event_loop().run_in_executor(None, client.ping, "healthcheck")
        except Exception as e:
            for task in asyncio.tasks.all_tasks():
                if not task.cancelled():
                    task.cancel("Trezor device has been disconnected")
            return
        await asyncio.sleep(1)


def run():
    import argparse
    parser = argparse.ArgumentParser(description='Command line interface for interaction with trezor password store.')
    parser.add_argument("--clear", action='store_true', help="clears saved application data")
    parser.add_argument("--store", type=str, help="specifies the store file to be used instead of remote store")
    parser.add_argument("--debug", action='store_true', help="print debug logs")
    args = parser.parse_args()

    if not args.debug:
        logging.disable()

    if args.clear:
        clear_data()
    elif args.store:
        asyncio.run(cli(FileSource(args.store)))
    else:
        asyncio.run(cli(DropboxSource()))


if __name__ == "__main__":
    run()
