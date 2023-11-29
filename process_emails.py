import base64
from typing import Dict, List, Optional, Union, Tuple
from googleapiclient.discovery import build, Resource
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from openai import OpenAI
import os
from google.oauth2.credentials import Credentials
from llama_cpp import Llama
from colorama import Fore
from dotenv import load_dotenv
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LOCAL_LLAMA_LOCATION = os.getenv("LOCAL_LLAMA_LOCATION")

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

class LanguageModelClient:
    def __init__(self, model_name: str):
        self.model_name = model_name

    def create_chat_completion(self, messages: list, max_tokens: int):
        raise NotImplementedError

class OpenAIClient(LanguageModelClient):
    def __init__(self, api_key: str):
        super().__init__(model_name="gpt-4-1106-preview")
        self.client = OpenAI(api_key=api_key)

    def create_chat_completion(self, messages: list, max_tokens: int):
        return self.client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.0,
        )

# Subclass for Llama
class LlamaClient(LanguageModelClient):
    def __init__(self, model_path: str, n_gpu_layers: int, n_ctx: int, n_batch: int, chat_format: str, verbose: bool):
        super().__init__(model_name="Llama 2 7B")
        self.client = Llama(
            model_path=model_path,
            n_gpu_layers=n_gpu_layers,
            n_ctx=n_ctx,
            n_batch=n_batch,
            chat_format=chat_format,
            verbose=verbose,
        )

    def create_chat_completion(self, messages: list, max_tokens: int):
        response = self.client.create_chat_completion(messages=messages)
        return response


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


def get_user_name():
    user_first_name = input("Enter your first name: ")
    user_last_name = input("Enter your last name: ")
    return user_first_name, user_last_name

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

def evaluate_email(email_data: Dict[str, Union[str, List[str]]], user_first_name: str, user_last_name: str, client: OpenAI) -> bool:
    MAX_EMAIL_LEN = 3000
    system_message: Dict[str, str] = {
        "role": "system",
        "content": (
            "Your task is to assist in managing the Gmail inbox of a busy individual, "
            f"{user_first_name} {user_last_name}, by filtering out promotional emails "
            "from their personal (i.e., not work) account. Your primary focus is to ensure "
            "that emails from individual people, whether they are known family members (with the "
            f"same last name), close acquaintances, or potential contacts {user_first_name} might be interested "
            "in hearing from, are not ignored. You need to distinguish between promotional, automated, "
            "or mass-sent emails and personal communications.\n\n"
            "Respond with \"True\" if the email is promotional and should be ignored based on "
            "the below criteria, or \"False\" otherwise. Remember to prioritize personal "
            "communications and ensure emails from genuine individuals are not filtered out.\n\n"
            "Criteria for Ignoring an Email:\n"
            "- The email is promotional: It contains offers, discounts, or is marketing a product "
            "or service.\n"
            "- The email is automated: It is sent by a system or service automatically, and not a "
            "real person.\n"
            "- The email appears to be mass-sent or from a non-essential mailing list: It does not "
            f"address {user_first_name} by name, lacks personal context that would indicate it's personally written "
            "to her, or is from a mailing list that does not pertain to her interests or work.\n\n"
            "Special Consideration:\n"
            "- Exception: If the email is from an actual person, especially a family member (with the "
            f"same last name), a close acquaintance, or a potential contact {user_first_name} might be interested in, "
            "and contains personalized information indicating a one-to-one communication, do not mark "
            "it for ignoring regardless of the promotional content.\n\n"
            "- Additionally, do not ignore emails requiring an action to be taken for important matters, "
            "such as needing to send a payment via Venmo, but ignore requests for non-essential actions "
            "like purchasing discounted items or signing up for rewards programs.\n\n"
            "Be cautious: If there's any doubt about whether an email is promotional or personal, "
            "respond with \"False\".\n\n"
            "The user message you will receive will have the following format:\n"
            "Subject: <email subject>\n"
            "To: <to names, to emails>\n"
            "From: <from name, from email>\n"
            "Cc: <cc names, cc emails>\n"
            "Gmail labels: <labels>\n"
            "Body: <plaintext body of the email>\n\n"
            "Your response must be:\n"
            "\"True\" or \"False\""
        )
    }
    truncated_body = email_data['body'][:MAX_EMAIL_LEN] + ("..." if len(email_data['body']) > MAX_EMAIL_LEN else "")
    user_message: Dict[str, str] = {
        "role": "user",
        "content": (
            f"Subject: {email_data['subject']}\n"
            f"To: {email_data['to']}\n"
            f"From: {email_data['from']}\n"
            f"Cc: {email_data['cc']}\n"
            f"Gmail labels: {email_data['labels']}\n"
            f"Body: {truncated_body}"
        )
    }

    # Send the messages to GPT-4, TODO add retry logic
    try:
        completion = client.create_chat_completion(
            messages=[system_message, user_message],
            max_tokens=1
        )
    except Exception as e:
        print(f"Failed to evaluate email: {e}")
        return False

    # Extract and return the response
    if isinstance(client, OpenAIClient):
        return completion.choices[0].message.content.strip() == "True"
    elif isinstance(client, LlamaClient):
        return completion['choices'][0]['message']['content'].strip() == "True"





def process_email(gmail: Resource, message_info: Dict[str, Union[str, List[str]]], email_data_parsed: Dict[str, Union[str, List[str]]], user_first_name: str, user_last_name: str, client: OpenAI) -> int:
    # Evaluate email
    if evaluate_email(email_data_parsed, user_first_name, user_last_name, client):
        print(Fore.LIGHTYELLOW_EX + "Email is not worth the time, marking as read" + Fore.RESET)
        # Remove UNREAD label
        try:
            gmail.users().messages().modify(
                userId='me',
                id=message_info['id'],
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            print(Fore.LIGHTGREEN_EX + "Email marked as read successfully" + Fore.RESET)
            return 1
        except Exception as e:
            print(Fore.LIGHTRED_EX + f"Failed to mark email as read: {e}" + Fore.RESET)
    else:
        print(Fore.LIGHTBLUE_EX + "Email is worth the time, leaving as unread" + Fore.RESET)
    return 0

def report_statistics(total_unread_emails: int, total_pages_fetched: int, total_marked_as_read: int, model_used: str) -> None:
    print("\n")  
    table_header = f"{Fore.LIGHTCYAN_EX}{'Statistics':<35}{'Value':<15}{Fore.RESET}"
    table_divider = f"{Fore.LIGHTCYAN_EX}{'-' * 50}{Fore.RESET}"
    table_rows = [
        f"{Fore.LIGHTYELLOW_EX}{'Total unread emails fetched':<35}{total_unread_emails:<15}{Fore.RESET}",
        f"{Fore.LIGHTYELLOW_EX}{'Total pages fetched':<35}{total_pages_fetched:<15}{Fore.RESET}",
        f"{Fore.LIGHTYELLOW_EX}{'Total emails marked as read':<35}{total_marked_as_read:<15}{Fore.RESET}",
        f"{Fore.LIGHTYELLOW_EX}{'Final number of unread emails':<35}{total_unread_emails - total_marked_as_read:<15}{Fore.RESET}",
        f"{Fore.LIGHTYELLOW_EX}{'Language model used':<35}{model_used:<15}{Fore.RESET}"
    ]
    print(table_header)
    print(table_divider)
    for row in table_rows:
        print(row)

def main():
    gmail = get_gmail_service()

    # Ask the user which language model client to use
    client_type = input("Enter 'openai' or 'llama' to choose the language model: ").lower()
    if client_type == 'openai':
        client = OpenAIClient(api_key=OPENAI_API_KEY)
    elif client_type == 'llama':
        client = LlamaClient(
            model_path=LOCAL_LLAMA_LOCATION, #your local llama location
            n_gpu_layers=60,
            n_ctx=3584,
            n_batch=521,
            chat_format="llama-2",
            verbose=False
        )
    else:
        raise ValueError("Invalid language model type selected.")

    user_first_name, user_last_name = get_user_name()

    page_token: Optional[str] = None

    total_unread_emails = 0
    total_pages_fetched = 0
    total_marked_as_read = 0

    while True:  # Continue looping until no more pages of messages
        # Fetch unread emails
        messages, page_token = fetch_emails(gmail, page_token)
        total_pages_fetched += 1
        print(f"Fetched page {total_pages_fetched} of emails")

        total_unread_emails += len(messages)
        for message_info in messages:  # TODO process emails on a single page in parallel
            # Fetch and parse email data
            email_data_parsed = parse_email_data(gmail, message_info)

            # Process email
            total_marked_as_read += process_email(gmail, message_info, email_data_parsed, user_first_name, user_last_name, client)

        if not page_token:
            break  # Exit the loop if there are no more pages of messages

    report_statistics(total_unread_emails, total_pages_fetched, total_marked_as_read, client.model_name)

if __name__ == "__main__":
    main()