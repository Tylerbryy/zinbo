from typing import Optional
import os

from dotenv import load_dotenv
from src.language_model_client import OpenAIClient, LlamaClient

from src.gmail_service import get_gmail_service, fetch_emails, parse_email_data
from src.email_processing import process_email, report_statistics

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LOCAL_LLAMA_LOCATION = os.getenv("LOCAL_LLAMA_LOCATION")


def get_user_name():
    user_first_name = input("Enter your first name: ")
    user_last_name = input("Enter your last name: ")
    return user_first_name, user_last_name


def main():
    gmail = get_gmail_service()

    # Ask the user which language model client to use
    client_type = input("Enter 'openai' or 'llama' to choose the language model: ").lower()
    if client_type == 'openai':
        client = OpenAIClient(api_key=OPENAI_API_KEY)
    elif client_type == 'llama':
        client = LlamaClient(
            model_path=LOCAL_LLAMA_LOCATION, #your local llama location
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