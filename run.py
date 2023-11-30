from typing import Optional
import os

from dotenv import load_dotenv
from src.language_model_client import OpenAIClient, LlamaClient, HermesClient

from src.gmail_service import get_gmail_service, fetch_emails, parse_email_data
from src.email_processing import process_email, report_statistics

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LOCAL_LLAMA_LOCATION = os.getenv("LOCAL_LLAMA_LOCATION")
LOCAL_OPEN_HERMES_LOCATION = os.getenv("LOCAL_OPEN_HERMES_LOCATION")

def get_user_name():
    user_first_name = input("Enter your first name: ")
    user_last_name = input("Enter your last name: ")
    return user_first_name, user_last_name

class LanguageModelClientFactory:
    @staticmethod
    def get_client(client_type: str, **kwargs):
        if client_type == 'gpt-4-1106-preview':
            return OpenAIClient(api_key=kwargs.get("api_key"))
        elif client_type == 'llama-2-7B':
            return LlamaClient(
                model_path=kwargs.get("model_path", LOCAL_LLAMA_LOCATION),
                n_ctx=kwargs.get("n_ctx", 3584),
                n_batch=kwargs.get("n_batch", 521),
                chat_format=kwargs.get("chat_format", "llama-2"),
                verbose=kwargs.get("verbose", False)
            )
        elif client_type == 'openhermes-2.5-mistral-7b':
            return HermesClient(
                model_path=kwargs.get("model_path", LOCAL_OPEN_HERMES_LOCATION),
                n_ctx=kwargs.get("n_ctx", 2048),
                n_batch=kwargs.get("n_batch", 1),
                chat_format=kwargs.get("chat_format", "llama-2"),
                verbose=kwargs.get("verbose", False)
            )
        else:
            raise ValueError(f"Invalid language model type selected: {client_type}")
        
def choose_language_model_client():
    clients = {
        '1': ('gpt-4-1106-preview', OPENAI_API_KEY),
        '2': ('llama-2-7B', LOCAL_LLAMA_LOCATION),
        '3': ('openhermes-2.5-mistral-7b', LOCAL_OPEN_HERMES_LOCATION)
    }

    print("Please choose the language model client you want to use:")
    print("1: gpt-4-1106-preview")
    print("2: llama-2-7B")
    print("3: openhermes-2.5-mistral-7b")
    
    choice = input("Enter the number of your choice: ").strip()

    while choice not in clients:
        print("Invalid choice. Please try again.")
        choice = input("Enter the number of your choice: ").strip()

    client_type, model_path_or_key = clients[choice]
    return client_type, model_path_or_key

def main():
    gmail = get_gmail_service()

    # Ask the user which language model client to use
    client_type, model_path_or_key = choose_language_model_client()
    client_kwargs = {
        'api_key': model_path_or_key if client_type == 'gpt-4-1106-preview' else None,
        'model_path': model_path_or_key if client_type in ['llama-2-7B', 'openhermes-2.5-mistral-7b'] else None
    }
    client = LanguageModelClientFactory.get_client(client_type, **client_kwargs)


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