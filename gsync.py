from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

f = open('emails_truncated')

emails = []
for line in f:
    emails.append(line.rstrip())

def callback(request_id, response, exception):
    if exception:
        # Handle error
        print(exception)
    else:
        print("Permission Id: %s" % response.get('id'))

def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)
    
    page_token = None

    # Call the Drive v3 API
    results = service.drives().list(
        fields="nextPageToken, drives(id, name)",pageToken=page_token).execute()
    items = results.get('drives', [])

    if not items:
        print('No files found.')
    else:
        print('Drives:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))
    share_id = '0AHU3BFQXRAc7Uk9PVA'
    batch = service.new_batch_http_request(callback=callback)
    for email in emails:
        user_permission = {
            'type': 'user',
            'role': 'reader',
            'emailAddress': email
        }
        batch.add(service.permissions().create(
                fileId=share_id,
                body=user_permission,
                supportsAllDrives = True,
                fields='id',
        ))
    batch.execute()


if __name__ == '__main__':
    main()
