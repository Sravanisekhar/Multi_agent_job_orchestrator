import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from utils.gmail_client import GmailVerificationHandler

def test_auth():
    print("Initializing Gmail authentication...")
    # This will open your browser window the first time to let you log in and approve permissions
    handler = GmailVerificationHandler(
        credentials_path="config/credentials.json",
        token_path="config/token.json"
    )
    print("Gmail authentication successful! token.json generated.")

if __name__ == "__main__":
    test_auth()