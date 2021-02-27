import os
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive.appdata',
]


def set_client_secret_files(path_to_file):
    creds_file = os.path.abspath(path_to_file)
    with open('credentials.txt', 'w+') as file:
        file.write(creds_file)


def get_path_to_client_secret_file():
    if os.path.exists('credentials.txt'):
        with open('credentials.txt', 'r+') as file:
            client_secret_file = file.read()
    else:
        raise FileExistsError('File "credentials.txt" not found.\n '
                              'Please use --set_secret_file to specify the path to the client_secret_file')
    return client_secret_file


def get_credentials():
    credentials = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            client_secret_file = get_path_to_client_secret_file()
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, SCOPES)
            credentials = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)
    return credentials


def get_drive_service():
    credentials = get_credentials()
    drive_service = build('drive', 'v3', credentials=credentials)
    return drive_service
