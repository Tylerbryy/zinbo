import subprocess
import os
from huggingface_hub import hf_hub_download


# Define the path to your .env file
env_file_path = '.env'
models_dir = 'models'  # Define the models directory

# Ensure the models directory exists
os.makedirs(models_dir, exist_ok=True)

# Detect the operating system and set the environment variable for symlinks if on Windows
if os.name == 'nt':   
    os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'


# Function to install dependencies from requirements.txt
def install_requirements():
    subprocess.check_call(["pip", "install", "-r", "requirements.txt"])
# Function to update the .env file with the new model path
def update_env_file(key, new_value):
    # Check if the .env file exists
    if os.path.exists(env_file_path):
        # Read the current contents of the file
        with open(env_file_path, 'r') as file:
            lines = file.readlines()

        # Update the specified key with the new value
        with open(env_file_path, 'w') as file:
            found = False
            for line in lines:
                if line.startswith(key):
                    file.write(f'{key}="{new_value}"\n')
                    found = True
                else:
                    file.write(line)
            if not found:
                file.write(f'{key}="{new_value}"\n')
    else:
        # Create the .env file if it does not exist
        with open(env_file_path, 'w') as file:
            file.write(f'{key}="{new_value}"\n')

def update_operating_system_env():
    # Detect the operating system
    operating_system = 'Mac' if os.name == 'posix' else 'Windows'
    
    # Update the .env file with the detected operating system
    update_env_file('OPERATING_SYSTEM', operating_system)

# Call the function to update the OPERATING_SYSTEM environment variable
update_operating_system_env()


# Function to download models from Hugging Face and update .env
def download_models():
    # Define the model repository IDs and filenames
    models = {
        'TheBloke/OpenHermes-2.5-Mistral-7B-GGUF': ('openhermes-2.5-mistral-7b.Q4_K_M.gguf', 'LOCAL_OPEN_HERMES_LOCATION'),
        'TheBloke/Llama-2-7B-Chat-GGUF': ('llama-2-7b-chat.Q4_K_M.gguf', 'LOCAL_LLAMA_LOCATION'),
        # Add more models here if necessary
    }

    # Download each model and update the .env file
    for repo_id, (filename, env_key) in models.items():
        print(f"Downloading {filename} from {repo_id}...")
        
        model_path = hf_hub_download(repo_id=repo_id, filename=filename, cache_dir=models_dir)
        
        # Update the .env file with the new model path
        update_env_file(env_key, model_path)

# Post-installation: Install requirements and download models
install_requirements()
download_models()