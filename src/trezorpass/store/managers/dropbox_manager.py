from datetime import datetime
from pathlib import Path
import json
import os

import dropbox
import appdirs
from InquirerPy import inquirer

from trezorpass.store.managers.manager import Manager
from trezorpass.utils import APP_DIR

DROPBOX_APP_KEY = "s340kh3l0vla1nv" # APP_KEY of the official TPM, potentionally breaking if maintainers disable PKCE flow for Dropbox auth
DROPBOX_TOKEN_FILE = os.path.join(APP_DIR, 'dropbox')

class DropboxManager(Manager):
    def __init__(self, filename: str):
        self.filename = filename
        try:
            with open(DROPBOX_TOKEN_FILE, 'r') as file:
                self.oauth = json.load(file)
        except:
            self.oauth = None

    async def authenticate(self):
        oauth_result = None
        while not oauth_result:
            auth_flow = dropbox.DropboxOAuth2FlowNoRedirect(DROPBOX_APP_KEY, use_pkce=True, token_access_type='offline')
            authorize_url = auth_flow.start()
            print("1. Go to: " + authorize_url)
            print("2. Click \"Allow\" (you might have to log in first).")
            print("3. Copy the authorization code.")
            auth_code = await inquirer.text("Enter the authorization code here:").execute_async()
            try:
                oauth_result = auth_flow.finish(auth_code)
            except:
                retry = await inquirer.confirm("Invalid authorization code, retry?").execute_async()
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
    async def password_store(self) -> bytes:
        if not self.oauth:
            await self.authenticate()
        with dropbox.Dropbox(
            oauth2_access_token=self.oauth["access_token"],
            oauth2_refresh_token=self.oauth["refresh_token"],
            oauth2_access_token_expiration=datetime.fromisoformat(self.oauth["expiration"]),
            app_key=DROPBOX_APP_KEY
        ) as dbx:
            (_, response) = dbx.files_download("/" + self.filename)
            return response.content