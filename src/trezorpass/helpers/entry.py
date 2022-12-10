from typing import List
import webbrowser

from trezorlib.client import TrezorClient
from InquirerPy import inquirer
from pyperclip import copy

from ..store import Entry
from ..utils import prompt_print


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
                prompt_print("Username has been copied to the clipboard")
            elif action == choices[2]:
                clipboard_dirty = True
                copy(entry.password_cleartext(client))
                prompt_print("Password has been copied to the clipboard")
            elif action == choices[3]:
                print(entry.show(client))
            elif action == choices[4]:
                print(entry.show(client, secrets=True))
    except KeyboardInterrupt:
        pass
    finally:
        if clipboard_dirty:
            prompt_print("Cleaning up the clipboard")
            copy("")