import subprocess
import json
from urllib.parse import urlparse
import argparse

from trezorlib.misc import encrypt_keyvalue, decrypt_keyvalue
from trezorlib.tools import parse_path
from trezorlib.client import get_default_client


PATH = "m/10016'/0"

def get_master_key() -> str:
    client = get_default_client()
    address_n = parse_path(PATH)
    key = "Activate TREZOR Password Manager?"
    value = bytes.fromhex("2d650551248d792eabf628f451200d7f51cb63e46aadcbb1038aacb05e8c8aee2d650551248d792eabf628f451200d7f51cb63e46aadcbb1038aacb05e8c8aee")
    return encrypt_keyvalue(client, address_n, key, value).hex()

def decrypt(key, data) -> bytes:
    proc = subprocess.run(["node", "decrypt.js", key], input=data, capture_output=True)
    return proc.stdout

def decrypt_file(filepath):
    master_key = get_master_key()
    enc_key = master_key[len(master_key) // 2:]
    with open(filepath, 'rb') as file:
        return json.loads(decrypt(enc_key, file.read()).decode('utf8'))

def select_entry(entries):
    print("Following entries were found:")
    for key in entries:
        print(f"{key}: {entries[key]['title']}")
    choice = input("Select entry: ")
    return entries[choice]

def get_entry_key(entry):
    client = get_default_client()
    address_n = parse_path("m/10016'/0")
    domain = urlparse(entry["title"]).netloc
    key = f'Unlock {domain} for user {entry["username"]}?'
    value = bytes.fromhex(entry["nonce"])
    return decrypt_keyvalue(client, address_n, key, value, ask_on_encrypt=False).hex()

def decrypt_entry(entry):
    enc_key = get_entry_key(entry)
    copy = entry.copy()
    copy["password"] = decrypt(enc_key, bytes(entry["password"]["data"])).decode("utf8")
    copy["safe_note"] = decrypt(enc_key, bytes(entry["safe_note"]["data"])).decode("utf8")
    return copy

def run(filepath):
    data = decrypt_file(filepath)
    while True:
        selected_entry = select_entry(data['entries'])
        decrypted_entry = decrypt_entry(selected_entry)
        print(decrypted_entry)
        if input("Decrypt another entry? [y/n]: ") != 'y':
            break

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('filepath', type=str, help='Path to the password store file')
    args = parser.parse_args()
    run(args.filepath)