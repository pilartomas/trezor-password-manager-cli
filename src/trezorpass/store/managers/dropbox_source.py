import logging
from datetime import datetime
import json
import os

import dropbox
from InquirerPy import inquirer

from trezorpass.store.managers.source import Source, SourceError
from trezorpass.appdata import APP_DIR

DROPBOX_APP_KEY = "s340kh3l0vla1nv"  # APP_KEY of the official TPM, potentially breaking if maintainers disable
# PKCE flow for Dropbox auth
DROPBOX_TOKEN_FILE = os.path.join(APP_DIR, 'dropbox')


class OAuth:
    def __init__(self, access_token: str = None, refresh_token: str = None, expiration: str = None):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expiration = expiration

    @staticmethod
    def load():
        oauth = OAuth()
        with open(DROPBOX_TOKEN_FILE, 'r') as file:
            oauth.__dict__ = json.load(file)
            return oauth

    def store(self):
        with open(DROPBOX_TOKEN_FILE, 'w+') as file:
            os.chmod(DROPBOX_TOKEN_FILE, 0o600)
            file.write(json.dumps(self.__dict__))


class DropboxSource(Source):
    def __init__(self):
        try:
            self.oauth = OAuth.load()
        except Exception as e:
            self.oauth = None

    @staticmethod
    async def authenticate():
        auth_flow = dropbox.DropboxOAuth2FlowNoRedirect(DROPBOX_APP_KEY, use_pkce=True, token_access_type='offline')
        authorize_url = auth_flow.start()
        print("1. Go to: " + authorize_url)
        print("2. Click \"Allow\" (you might have to log in first).")
        print("3. Copy the authorization code.")
        oauth_result = None
        while not oauth_result:
            auth_code = await inquirer.text("Enter the authorization code here:").execute_async()
            try:
                oauth_result = auth_flow.finish(auth_code)
            except:
                retry = await inquirer.confirm("Invalid authorization code, retry?").execute_async()
                if not retry:
                    raise SourceError()
        oauth = OAuth(oauth_result.access_token, oauth_result.refresh_token, oauth_result.expires_at.isoformat())
        try:
            oauth.store()
        except Exception as ex:
            logging.exception("Unable to store the oauth tokens")
        return oauth

    async def load_store(self, store_name) -> bytes:
        if not self.oauth:
            self.oauth = await self.authenticate()
        with dropbox.Dropbox(
                oauth2_access_token=self.oauth.access_token,
                oauth2_refresh_token=self.oauth.refresh_token,
                oauth2_access_token_expiration=datetime.fromisoformat(self.oauth.expiration),
                app_key=DROPBOX_APP_KEY
        ) as dbx:
            (_, response) = dbx.files_download("/" + store_name)
            return response.content
