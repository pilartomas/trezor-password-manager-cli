from typing import List
import asyncio
import webbrowser
import shutil

from trezorlib.client import TrezorClient
from trezorlib.transport import TransportException, DeviceIsBusy
from trezorlib.exceptions import Cancelled, PinException

from InquirerPy import inquirer

from pyperclip import copy

from trezorpass.client import get_safe_client
from trezorpass.entry import Entry
from trezorpass.store import Store
from trezorpass.store.store import StoreDecodeError, StoreDecryptError
from trezorpass.utils import APP_DIR, animate_dots, welcome, goodbye

async def select_entry(entries: List[Entry], long_instruction: str) -> Entry:
    '''Selects an entry'''
    choices = [{"value": entry, "name":entry.note if entry.note is not None else entry.title} for entry in entries]
    selection = await inquirer.fuzzy(
        message="Select an entry:",
        choices=choices,
        long_instruction=long_instruction
    ).execute_async()
    return selection

healthcheck_tasks = set()
async def get_client() -> TrezorClient:
    '''Gets the Trezor client'''
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
        except (TransportException, DeviceIsBusy):
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
            action = await inquirer.select("Select an action:", ['Open the URL', 'Copy username to clipboard', 'Copy password to clipboard', 'Show entry', 'Show entry including secrets'], long_instruction=long_instruction).execute_async()
            if action == "Show entry":
                print(entry.show(client))
            elif action == "Copy username to clipboard":
                copy(entry.username)
                print("Username has been copied to the clipboard")
            elif action == "Copy password to clipboard":
                clipboard_dirty = True
                copy(entry.password_cleartext(client))
                print("Password has been copied to the clipboard")
            elif action == "Open the URL":
                webbrowser.open(entry.url, 2)
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
            try:
                client.end_session()
            except:
                pass
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

def clear_data():
    shutil.rmtree(APP_DIR, ignore_errors=True)

def run():
    import argparse
    parser = argparse.ArgumentParser(description = 'Command line interface for interaction with trezor password store.')
    parser.add_argument("--clear", action='store_true', help="clears saved application data")
    args = parser.parse_args()
    
    if args.clear:
        clear_data()
    else:
        asyncio.run(cli())

if __name__ == "__main__":
    run()