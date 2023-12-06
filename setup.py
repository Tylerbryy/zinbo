import os
import subprocess
from huggingface_hub import hf_hub_download


# Define paths
env_file_path = ".env"
models_dir = "models"


def ensure_models_dir():
    os.makedirs(models_dir, exist_ok=True)


# Detect and handle OS-specific environment variables
def detect_os():
    os_name = os.name
    if os_name == "nt":
        os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
    return "Mac" if os_name == "posix" else "Windows"


# Install dependencies
def install_requirements():
    subprocess.check_call(["pip", "install", "-r", "requirements.txt"])


# Update .env file
def update_env(key, new_value):
    # Read and update existing content
    if os.path.exists(env_file_path):
        with open(env_file_path, "r") as f:
            lines = f.readlines()

        with open(env_file_path, "w") as f:
            found = False
            for line in lines:
                if line.startswith(f"{key}="):
                    f.write(f"{key}={new_value}\n")
                    found = True
                else:
                    f.write(line)
        if not found:
            f.write(f"{key}={new_value}\n")
    # Create new .env file
    else:
        with open(env_file_path, "w") as f:
            f.write(f"{key}={new_value}\n")


# Download and update models
def download_models():
    # Model data
    models = {
        "TheBloke/OpenHermes-2.5-Mistral-7B-GGUF": ("openhermes-2.5-mistral-7b.Q4_K_M.gguf", "LOCAL_OPEN_HERMES_LOCATION"),
        "TheBloke/Llama-2-7B-Chat-GGUF": ("llama-2-7b-chat.Q4_K_M.gguf", "LOCAL_LLAMA_LOCATION"),
    }

    # Download and update
    for repo_id, (filename, env_key) in models.items():
        print(f"Downloading {filename} from {repo_id}...")

        model_path = hf_hub_download(repo_id=repo_id, filename=filename, cache_dir=models_dir)

        update_env(env_key, model_path)


# Main execution
ensure_models_dir()
operating_system = detect_os()
install_requirements()
update_env("OPERATING_SYSTEM", operating_system)
download_models()
