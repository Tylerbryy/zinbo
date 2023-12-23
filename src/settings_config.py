from colorama import Fore
import json
import os 

SETTINGS_DIR = 'settings'  # Define the settings directory name

def ensure_settings_dir_exists():
    os.makedirs(SETTINGS_DIR, exist_ok=True)  # Create the settings directory if it doesn't exist

def save_user_settings(settings, file_name='user_settings.json'):
    ensure_settings_dir_exists()  # Ensure the settings directory exists
    file_path = os.path.join(SETTINGS_DIR, file_name)  # Construct the full file path
    with open(file_path, 'w') as file:
        json.dump(settings, file)

def load_user_settings(file_name='user_settings.json'):
    file_path = os.path.join(SETTINGS_DIR, file_name)  # Construct the full file path
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return None

def ask_to_override_settings(settings):
    os.system('clear' if os.name == 'posix' else 'cls')
    print(Fore.LIGHTYELLOW_EX + "Last used settings found:" + Fore.RESET)
    print()
    for key, value in settings.items():
        # Mask the value if it is a string longer than 25 characters
        if isinstance(value, str) and len(value) > 25:
            masked_value = '*' * (len(value) - 15) + value[-15:]
        else:
            masked_value = value
        print(Fore.LIGHTYELLOW_EX + f"- {key}: {masked_value}" + Fore.RESET)
    choice = input(Fore.LIGHTYELLOW_EX + "Do you want to use these settings? (yes/no): " + Fore.RESET).strip().lower()
    return choice == 'yes'