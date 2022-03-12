import dropbox

from .manager import Manager

APP_KEY = "s340kh3l0vla1nv" # APP_KEY of the official TPM, potentionally breaking if maintainers disable PKCE flow for Dropbox auth

class DropboxManager(Manager):
    def __init__(self):
        self.oauth = None

    def authenticate(self):
        auth_flow = dropbox.DropboxOAuth2FlowNoRedirect(APP_KEY, use_pkce=True, token_access_type='offline')
        authorize_url = auth_flow.start()
        print("1. Go to: " + authorize_url)
        print("2. Click \"Allow\" (you might have to log in first).")
        print("3. Copy the authorization code.")
        auth_code = input("Enter the authorization code here: ").strip()
        oauth_result = auth_flow.finish(auth_code)
        self.oauth = oauth_result

    def get_password_store(self, filename: str) -> bytes:
        if not self.oauth:
            self.authenticate()
        with dropbox.Dropbox(oauth2_access_token=self.oauth.access_token) as dbx:
            (_, response) = dbx.files_download("/" + filename)
            return response.content