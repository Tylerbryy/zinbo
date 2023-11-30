# Inbox Cleaner

This script helps manage a Gmail inbox by filtering out promotional emails using GPT-3, GPT-4, or Llama 2 7B.
![Inbox Cleaner Logo](public/logo.png)

## Prerequisites

- Python 3.7 or higher
- Gmail account
- Google Cloud account with Gmail API enabled
- OpenAI API key
- Llama model (if using Llama)

## Setup

1. Clone this repository:

   ```
   git clone https://github.com/Tylerbryy/email_inbox_cleaner.git
   cd inbox_cleaner
   ```

2. Install the required Python packages:

   ```
   pip install -r requirements.txt
   ```

3. Set up your Google API credentials:

   - Follow the instructions [here](https://developers.google.com/workspace/guides/create-credentials) to create a new OAuth 2.0 Client ID.
   - Download the JSON file and rename it to `credentials.json`.
   - Put `credentials.json` in the `inbox_cleaner` directory.

4. Set up your OpenAI API key and Llama model path (if using Llama) by creating a `.env` file in the `inbox_cleaner` directory with the following content:


   - Follow the instructions [here](https://platform.openai.com/api-keys) to get your OpenAI API key.
   - Set the key as an environment variable:

     ```
      OPENAI_API_KEY=your_openai_api_key
      LOCAL_LLAMA_LOCATION=path_to_your_local_llama_model
     ```
   Replace `your_openai_api_key` with your actual OpenAI API key and `path_to_your_local_llama_model` with the file path to your Llama model.

## Usage

Run the script:

```
run.py
```

When prompted, enter your first and last name. The script will then start processing your unread emails.
