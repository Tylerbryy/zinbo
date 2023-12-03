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

2. Install the required Python packages:

   ```
   pip install -r requirements.txt
   ```

3. Set up your Google API credentials:

   - Follow the instructions [here](https://developers.google.com/workspace/guides/create-credentials) to create a new OAuth 2.0 Client ID.
   - Download the JSON file and rename it to `credentials.json`.
   - Put `credentials.json` in the `zinbo` directory.

4. Set up your environment variables by copying the `.env.example` file to `.env` and filling in the values:

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
   - Set the key as an environment variable in the `.env` file along with the paths to your Llama and OpenHermes models.

## Usage

Run the script:

```
python run.py
```

When prompted, choose the language model client you want to use. The script will then start processing your unread emails.
