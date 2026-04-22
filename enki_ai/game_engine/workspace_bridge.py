import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Access Scopes
SCOPES = ['https://www.googleapis.com/auth/drive.readonly', 'https://www.googleapis.com/auth/documents.readonly']

class EnkiCloudBridge:
    def __init__(self):
        # Locate the root directory to find credentials
        self.base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.creds_path = os.path.join(self.base_path, 'credentials.json')
        self.token_path = os.path.join(self.base_path, 'token.json')
        
        self.creds = self.authenticate()
        self.drive_service = build('drive', 'v3', credentials=self.creds)
        self.docs_service = build('docs', 'v1', credentials=self.creds)

    def authenticate(self):
        creds = None
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.creds_path):
                    raise FileNotFoundError(f"🛡️ ARCHITECT: Place 'credentials.json' in {self.base_path}")
                
                flow = InstalledAppFlow.from_client_secrets_file(self.creds_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        return creds

    def audit_my_drive(self):
        results = self.drive_service.files().list(
            pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])
        print("\n[CLOUD] ☁️  ENKI CONNECTED TO WORKSPACE.")
        for item in items:
            print(f"[HUD] 📄 {item['name']}")
        return items

if __name__ == "__main__":
    bridge = EnkiCloudBridge()
    bridge.audit_my_drive()
