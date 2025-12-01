from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload
import os


class GDApi:

    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/drive']
        self.SERVICE_ACCOUNT_FILE = 'service_account.json'
        self.PARENT_FOLDER_ID = "1gDxYl-zN0HgqOXA4rIFXr8YPb4kNdZu4"

    def authenticate(self):
        creds = service_account.Credentials.from_service_account_file(self.SERVICE_ACCOUNT_FILE, scopes=self.SCOPES)
        return creds

    def upload(self, file_path):
        creds = self.authenticate()
        service = build('drive', 'v3', credentials=creds)

        file_name = os.path.basename(file_path)

        file_metadata = {
            'name': file_name,
            'parents': [self.PARENT_FOLDER_ID]
        }

        media = MediaFileUpload(file_path,
                                mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation')

        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id,webViewLink',
        ).execute()

        web_view_link = file.get('webViewLink')

        print("UPLOADED")
        return web_view_link



