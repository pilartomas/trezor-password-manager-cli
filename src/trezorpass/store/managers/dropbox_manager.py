from datetime import datetime
from pathlib import Path
import json
import os

import dropbox
import appdirs
from InquirerPy import inquirer

from trezorpass.store.managers.manager import Manager

DROPBOX_APP_KEY = "s340kh3l0vla1nv" # APP_KEY of the official TPM, potentionally breaking if maintainers disable PKCE flow for Dropbox auth
APP_DIR = appdirs.user_data_dir('trezor-pass')
DROPBOX_TOKEN_FILE = os.path.join(APP_DIR, 'dropbox')

class DropboxManager(Manager):
    def __init__(self):
        try:
            with open(DROPBOX_TOKEN_FILE, 'r') as file:
                self.oauth = json.load(file)
        except:
            self.oauth = None

    def authenticate(self):
        while not auth_code:
            auth_flow = dropbox.DropboxOAuth2FlowNoRedirect(DROPBOX_APP_KEY, use_pkce=True, token_access_type='offline')
            authorize_url = auth_flow.start()
            print("1. Go to: " + authorize_url)
            print("2. Click \"Allow\" (you might have to log in first).")
            print("3. Copy the authorization code.")
            try:
                auth_code = inquirer.text("Enter the authorization code here:")
                oauth_result = auth_flow.finish(auth_code)
            except:
                retry = inquirer.confirm("Invalid authorization code, retry?")
                if not retry:
                    raise Exception()
        self.oauth = {
            "access_token": oauth_result.access_token,
            "refresh_token": oauth_result.refresh_token,
            "expiration": oauth_result.expires_at.isoformat()
            }
        try:
            Path(APP_DIR).mkdir(parents=True)
            with open(DROPBOX_TOKEN_FILE, 'w+') as file:
                os.chmod(DROPBOX_TOKEN_FILE, 0o600)
                file.write(json.dumps(self.oauth))
        except Exception as ex:
            pass

    def get_password_store(self, filename: str) -> bytes:
        if not self.oauth:
            self.authenticate()
        else:
            token_found = True

        with dropbox.Dropbox(
            oauth2_access_token=self.oauth["access_token"],
            oauth2_refresh_token=self.oauth["refresh_token"],
            oauth2_access_token_expiration=datetime.fromisoformat(self.oauth["expiration"]),
            app_key=DROPBOX_APP_KEY
        ) as dbx:
            (_, response) = dbx.files_download("/" + filename)
            return response.content