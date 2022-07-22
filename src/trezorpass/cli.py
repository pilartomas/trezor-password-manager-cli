from typing import List
import time
import asyncio

from trezorlib.client import get_default_client, TrezorClient
from trezorlib.transport import TransportException
from trezorlib.exceptions import Cancelled, PinException, TrezorFailure

from InquirerPy import inquirer
from InquirerPy.utils import patched_print

from pyperclip import copy

from trezorpass.entry import Entry
from trezorpass.store import Store
from trezorpass.store.store import StoreDecodeError, StoreDecryptError
from trezorpass.utils import animate_dots, welcome, goodbye

async def select_entry(entries: List[Entry], long_instruction: str) -> Entry:
    '''Selects an entry'''
    choices = [{"value": entry, "name":entry.note if entry.note is not None else entry.title} for entry in entries]
    selection = await inquirer.fuzzy(
        message="Select an entry:",
        choices=choices,
        long_instruction=long_instruction
    ).execute_async()
    return selection

async def get_client() -> TrezorClient:
    '''Gets the Trezor client'''
    print("Looking for a Trezor device ", end="", flush=True)
    animation = animate_dots(5)
    while True:
        try:
            client = get_default_client()
            asyncio.get_event_loop().create_task(client_healthcheck(client))
            print()
            print("Trezor device ready")
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
        await asyncio.sleep(0.7)

async def load_store(client: TrezorClient) -> Store:
    while True:
        try:
            return await Store.load(client)
        except StoreDecryptError:
            print("Unable to decrypt the password store")
        except StoreDecodeError:
            print("Unable to decode the password store")
        except (KeyboardInterrupt, asyncio.CancelledError):
            raise
        except:
            print("Unable to load the password store")

async def manage_entry(entry: Entry, client: TrezorClient) -> None:
    clipboard_dirty = False
    try:
        long_instruction = "Press Ctrl+C to leave the entry"
        while True:
            action = await inquirer.select("Select an action:", ['Show entry', 'Copy to clipboard', 'Show entry including secrets'], long_instruction=long_instruction).execute_async()
            if action == "Show entry":
                print(entry.show(client))
            elif action == "Copy to clipboard":
                key = await inquirer.select("Select the value to copy:", ['username', 'password'], long_instruction=long_instruction).execute_async()
                if key == 'username':
                    copy(entry.username)
                elif key == 'password':
                    clipboard_dirty = True
                    copy(entry.password_cleartext(client))
                print(f"{key} has been copied to the clipboard")
            elif action == "Show entry including secrets":
                print(entry.show(client, secrets=True))
    except KeyboardInterrupt:
        pass
    finally:
        if clipboard_dirty:
            print("Cleaning up the clipboard")
            copy("")

async def cli():
    welcome()
    try:
        client = await get_client()
        store = await load_store(client)
        while True:
            try:
                entry = await select_entry(store.entries, long_instruction="Press Ctrl+C to exit")
                await manage_entry(entry, client)
            except Cancelled:
                print("Trezor operation has been cancelled")
            except PinException:
                print("Invalid pin")
    except KeyboardInterrupt:
        pass
    except asyncio.CancelledError as e:
        message = e.args[0] if len(e.args) > 0 else "Unexpected cancellation"
        print(message)
    except:
        print("Unexpected error")
        exit(1)
    finally:
        if client:
            client.end_session()
        goodbye()

async def client_healthcheck(client: TrezorClient):
    while True:
        try:
            await asyncio.get_event_loop().run_in_executor(None, client.ping, "healthcheck")
        except:
            for task in asyncio.tasks.all_tasks():
                if not task.cancelled():
                    task.cancel("Trezor device has been disconnected")
            return
        await asyncio.sleep(1)

def run_cli():
    asyncio.run(cli())

if __name__ == "__main__":
    run_cli()