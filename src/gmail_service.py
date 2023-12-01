import base64
from typing import Dict, List, Optional, Union, Tuple
from googleapiclient.discovery import build, Resource
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
from google.oauth2.credentials import Credentials


SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def get_user_email(gmail: Resource) -> str:
    profile = gmail.users().getProfile(userId='me').execute()
    return profile.get('emailAddress', '')

def fetch_emails(gmail: Resource, page_token: Optional[str]) -> Tuple[List[Dict[str, Union[str, List[str]]]], Optional[str]]:
    try:
        results = gmail.users().messages().list(
            userId='me',
            labelIds=['UNREAD'],
            pageToken=page_token  # Include the page token in the request if there is one
        ).execute()
    except Exception as e:
        print(f"Failed to fetch emails: {e}")
        return [], None

    messages: List[Dict[str, Union[str, List[str]]]] = results.get('messages', [])
    page_token = results.get('nextPageToken')
    return messages, page_token

def get_gmail_service():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)


def parse_email_data(gmail: Resource, message_info: Dict[str, Union[str, List[str]]]) -> Dict[str, Union[str, List[str]]]:
    # Fetch email data with 'full' format
    try:
        msg = gmail.users().messages().get(
            userId='me', 
            id=message_info['id'],
            format='full'
        ).execute()
    except Exception as e:
        print(f"Failed to fetch email data: {e}")
        return {}

    try:
        headers = msg['payload']['headers']
        subject = next(header['value'] for header in headers if header['name'] == 'Subject')
        to = next(header['value'] for header in headers if header['name'] == 'To')
        sender = next(header['value'] for header in headers if header['name'] == 'From')
        cc = next((header['value'] for header in headers if header['name'] == 'Cc'), None)
    except Exception as e:
        print(f"Failed to parse email data: {e}")
        return {}

    print(f"Fetched email - Subject: {subject}, Sender: {sender}")

    # Extract the plain text body
    parts = msg['payload'].get('parts', [])
    for part in parts:
        if part['mimeType'] == 'text/plain':
            body = part['body'].get('data', '')
            body = base64.urlsafe_b64decode(body.encode('ASCII')).decode('utf-8')
            break
    else:
        body = ''

    # Parse email data
    email_data_parsed: Dict[str, Union[str, List[str]]] = {
        'subject': subject,
        'to': to,
        'from': sender,
        'cc': cc,
        'labels': msg['labelIds'],
        'body': body,
    }
    return email_data_parsed