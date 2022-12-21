from typing import List
import webbrowser

from trezorlib.exceptions import Cancelled
from InquirerPy import inquirer
from pyperclip import copy

from trezorpass.store import Entry, EncryptedEntry, EntryDecrypter
from trezorpass.utils import prompt_print, prompt_print_pairs


async def select_entry(entries: List[Entry]) -> Entry:
    """Facilitates user interaction to select an entry from the given list of entries

    Returns:
        A single entry from the specified list of entries

    Raises:
        KeyboardInterrupt
    """
    choices = [{"value": entry, "name": entry.title} for entry in entries]
    selection = await inquirer.fuzzy(
        message="Select an entry:",
        choices=choices,
        long_instruction="Press Ctrl+C to exit"
    ).execute_async()
    return selection


async def manage_entry(entry: EncryptedEntry, decrypter: EntryDecrypter) -> None:
    """Facilitates interaction with the given entry"""
    clipboard_dirty = False
    try:
        while True:
            choices = [
                f'Open {entry.url}',
                'Copy username to clipboard',
                'Copy password to clipboard',
                'Show entry',
                'Show entry including secrets'
            ]
            action = await inquirer.select(
                "Select an action:",
                choices=choices,
                long_instruction="Press Ctrl+C to leave the entry"
                ).execute_async()
            try:
                if action == choices[0]:
                    webbrowser.open(entry.url, 2)
                elif action == choices[1]:
                    copy(entry.username)
                    prompt_print("Username has been copied to the clipboard")
                elif action == choices[2]:
                    decrypted_entry = decrypter.decrypt(entry)
                    copy(decrypted_entry.password)
                    clipboard_dirty = True
                    prompt_print("Password has been copied to the clipboard")
                elif action == choices[3]:
                    prompt_print_pairs([
                        ("URL", entry.url),
                        ("Title", entry.title),
                        ("Username", entry.username)
                    ])
                elif action == choices[4]:
                    decrypted_entry = decrypter.decrypt(entry)
                    prompt_print_pairs([
                        ("URL", decrypted_entry.url),
                        ("Title", decrypted_entry.title),
                        ("Username", decrypted_entry.username),
                        ("Password", decrypted_entry.password),
                        ("Safe Note", decrypted_entry.safe_note)
                    ])
            except Cancelled:
                prompt_print("Action has been cancelled")
    except KeyboardInterrupt:
        pass
    finally:
        if clipboard_dirty:
            prompt_print("Cleaning up the clipboard")
            copy("")
