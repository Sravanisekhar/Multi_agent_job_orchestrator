import os
import re
import time
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class GmailVerificationHandler:
    def __init__(self, credentials_path="config/credentials.json", token_path="config/token.json"):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.creds = None
        self._authenticate()

    def _authenticate(self):
        """Authenticates with Gmail API using OAuth2 Desktop App credentials."""
        if os.path.exists(self.token_path):
            self.creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"Please place your downloaded Google Cloud OAuth credentials JSON file at '{self.credentials_path}'"
                    )
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            with open(self.token_path, 'w') as token_file:
                token_file.write(self.creds.to_json())

        self.service = build('gmail', 'v1', credentials=self.creds)

    def fetch_latest_verification_code(self, sender_domain="", timeout_seconds=60):
        """
        Polls Gmail inbox for the newest incoming verification code/OTP within the last 'timeout_seconds'.
        """
        print(f"[GMAIL AGENT] Monitoring inbox for verification emails...")
        start_time = time.time()
        
        while time.time() - start_time < timeout_seconds:
            query = "is:unread verification OR code OR OTP"
            if sender_domain:
                query += f" from:{sender_domain}"

            results = self.service.users().messages().list(userId='me', q=query, maxResults=3).execute()
            messages = results.get('messages', [])

            if messages:
                for msg_ref in messages:
                    msg = self.service.users().messages().get(userId='me', id=msg_ref['id']).execute()
                    snippet = msg.get('snippet', '')
                    
                    # Extract 4 to 6 digit OTP patterns from snippet
                    code_match = re.search(r'\b\d{4,6}\b', snippet)
                    if code_match:
                        code = code_match.group(0)
                        print(f"[GMAIL AGENT] Verification code detected: {code}")
                        # Mark email as read
                        self.service.users().messages().batchModify(
                            userId='me',
                            body={'ids': [msg_ref['id']], 'removeLabelIds': ['UNREAD']}
                        ).execute()
                        return code

            time.sleep(5)  # Poll every 5 seconds
            
        print("[GMAIL AGENT] Timeout reached. No verification code found.")
        return None

if __name__ == "__main__":
    # Test script setup check
    print("Gmail Verification Handler initialized successfully.")