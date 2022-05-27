from datetime import datetime
from pathlib import Path
import json
import os

import dropbox
import appdirs
from InquirerPy import inquirer, get_style

from trezorpass.store.managers.manager import Manager
from trezorpass.utils import prompt_print

DROPBOX_APP_KEY = "s340kh3l0vla1nv" # APP_KEY of the official TPM, potentionally breaking if maintainers disable PKCE flow for Dropbox auth
APP_DIR = appdirs.user_data_dir('trezor-pass')
DROPBOX_TOKEN_FILE = os.path.join(APP_DIR, 'dropbox')
DROPBOX_PROMPT = "(dropbox)"

class DropboxManager(Manager):
    def __init__(self, filename: str):
        self.filename = filename
        try:
            with open(DROPBOX_TOKEN_FILE, 'r') as file:
                self.oauth = json.load(file)
        except:
            self.oauth = None

    def authenticate(self):
        oauth_result = None
        while not oauth_result:
            auth_flow = dropbox.DropboxOAuth2FlowNoRedirect(DROPBOX_APP_KEY, use_pkce=True, token_access_type='offline')
            authorize_url = auth_flow.start()
            prompt_print("1. Go to: " + authorize_url, DROPBOX_PROMPT)
            prompt_print("2. Click \"Allow\" (you might have to log in first).", DROPBOX_PROMPT)
            prompt_print("3. Copy the authorization code.", DROPBOX_PROMPT)
            auth_code = inquirer.text("Enter the authorization code here:", qmark=DROPBOX_PROMPT, amark=DROPBOX_PROMPT).execute()
            try:
                oauth_result = auth_flow.finish(auth_code)
            except:
                retry = inquirer.confirm("Invalid authorization code, retry?", qmark=DROPBOX_PROMPT, amark=DROPBOX_PROMPT).execute()
                if not retry:
                    raise Exception()
        self.oauth = {
            "access_token": oauth_result.access_token,
            "refresh_token": oauth_result.refresh_token,
            "expiration": oauth_result.expires_at.isoformat()
            }
        try:
            Path(APP_DIR).mkdir(parents=True, exist_ok=True)
            with open(DROPBOX_TOKEN_FILE, 'w+') as file:
                os.chmod(DROPBOX_TOKEN_FILE, 0o600)
                file.write(json.dumps(self.oauth))
        except Exception as ex:
            pass

    @property
    def password_store(self) -> bytes:
        if not self.oauth or not inquirer.confirm("Credentials found, proceed?", default=True, qmark=DROPBOX_PROMPT, amark=DROPBOX_PROMPT).execute():
            self.authenticate()

        with dropbox.Dropbox(
            oauth2_access_token=self.oauth["access_token"],
            oauth2_refresh_token=self.oauth["refresh_token"],
            oauth2_access_token_expiration=datetime.fromisoformat(self.oauth["expiration"]),
            app_key=DROPBOX_APP_KEY
        ) as dbx:
            (_, response) = dbx.files_download("/" + self.filename)
            return response.content