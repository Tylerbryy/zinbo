from typing import Dict, List, Union
from googleapiclient.discovery import Resource
from openai import OpenAI

from colorama import Fore
from src.email_evaluation import evaluate_email



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