<div alt style="text-align: center; transform: scale(.5);">
	<picture>
		<source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/tylerbryy/zinbo/main/public/logo2.png" />
		<img alt="tldraw" src="https://raw.githubusercontent.com/tylerbryy/zinbo/main/public/logo2.png" />
	</picture>
</div>

# Zinbo

Welcome to the Zinbo project.

## What is Zinbo?

Zinbo is a powerful tool designed to declutter your Gmail inbox by identifying and filtering out unwanted promotional emails. It leverages advanced language models such as GPT-3, GPT-4, [Llama 2 7B](https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF), and [OpenHermes 2.5 Mistral 7B](https://huggingface.co/TheBloke/OpenHermes-2.5-Mistral-7B-GGUF) to intelligently sort through your messages.


https://github.com/Tylerbryy/zinbo/assets/104282235/271c985e-4f4d-47f0-9812-91c03bbf435a



## Prerequisites

- Python 3.7 or higher
- Gmail account
- Google Cloud account with Gmail API enabled
- OpenAI API key
- Llama model (if using Llama)
- OpenHermes model (if using OpenHermes)

## Setup

1. Clone this repository:

   ```
   git clone https://github.com/Tylerbryy/zinbo.git
   cd zinbo
   ```

2. Set up your Google API credentials:

   - Follow the instructions [here](https://developers.google.com/workspace/guides/create-credentials) to create a new OAuth 2.0 Client ID.
   - Download the JSON file and rename it to `credentials.json`.
   - Put `credentials.json` in the `zinbo` directory.

3. Set up your environment variables by copying the `.env.example` file to `.env` and  just set your `OPENAI` key. The `setup.py` will fill out the rest. I left them as a option in case you want to modify the locations:

   For macOS/Linux:
   ```
   cp .env.example .env
   ```

   For Windows:
   ```
   copy .env.example .env
   ```
   - Edit the `.env` file with your actual values.
   - Follow the instructions [here](https://platform.openai.com/api-keys) to get your OpenAI API key.

4. Run

      ```bash
         python setup.py
      ```
5. You're done! Run the program!

      ```bash
         python run.py
      ```



## GPU Acceleration

`llama-cpp-python` supports various hardware acceleration backends. To enable GPU acceleration, set the `CMAKE_ARGS` environment variable before installing with `pip`. Below are instructions for different acceleration options:

#### OpenBLAS
For OpenBLAS support:
```bash
CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS" 
```
```
pip install llama-cpp-python  --upgrade --force-reinstall --no-cache-dir
```
#### cuBLAS (NVIDIA GPUs)
For cuBLAS support, ensure CUDA is installed and configured:
```bash
$env:CMAKE_ARGS="-DLLAMA_CUBLAS=on"
```
```
pip install llama-cpp-python  --upgrade --force-reinstall --no-cache-dir
```
#### Metal (MPS) for macOS
For Metal support on macOS:
```bash
CMAKE_ARGS="-DLLAMA_METAL=on"
```
```
pip install llama-cpp-python  --upgrade --force-reinstall --no-cache-dir
```
#### CLBlast
For CLBlast support:
```
CMAKE_ARGS="-DLLAMA_CLBLAST=on" 
```
```
pip install llama-cpp-python  --upgrade --force-reinstall --no-cache-dir
```

#### hipBLAS (AMD GPUs)
For hipBLAS / ROCm support on AMD GPUs:
```
CMAKE_ARGS="-DLLAMA_HIPBLAS=on"
```
```
pip install llama-cpp-python  --upgrade --force-reinstall --no-cache-dir
```
## Usage

Run the script:

```
python run.py
```

When prompted, choose the language model client you want to use. The script will then start processing your unread emails.
