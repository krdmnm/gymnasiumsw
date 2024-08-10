from googleapiclient.discovery import build
from google.oauth2 import service_account

# Google API kimlik bilgilerinizi ayarlayın
SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'path/to/service_account.json'  # Servis hesabı JSON dosyanız

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

service = build('calendar', 'v3', credentials=credentials)