from llama_cpp import Llama
from colorama import Fore, Style

# Initialize the Llama model with the specified parameters
llm = Llama(
    model_path=r"E:\ai\llm_models\lmstudio\TheBloke\OpenHermes-2.5-neural-chat-7B-v3-1-7B-GGUF\openhermes-2.5-neural-chat-7b-v3-1-7b.Q5_K_S.gguf",
    chat_format="chatml",
    n_gpu_layers=50,
    n_ctx=3584,
    n_batch=512,
)

# Initialize the conversation history with the system's role
conversation_history = [
    {"role": "system", "content": "You are a helpful assistant named Nova."}
]

# Start the conversation loop
while True:
    # Get user input and append it to the conversation history
    user_message = input(Fore.GREEN + "User: " + Style.RESET_ALL).strip()
    conversation_history.append({"role": "user", "content": user_message})

    # Generate a response from the Llama model
    response = llm.create_chat_completion(messages=conversation_history)

    # Extract the message content from the response
    message_content = response["choices"][0]["message"]["content"].strip()

    # Replace any unwanted tokens or formatting tags
    message_content = message_content.replace("[INST]", "").replace("<<SYS>>", "").replace("</SYS>", "").replace("<</A>", "").replace("<@A>", "").replace("[/INST]", "")

    # Print the model's response with appropriate color formatting
    print(Fore.CYAN + "Nova: " + Style.RESET_ALL + message_content)

    # Append the model's response to the conversation history
    conversation_history.append({"role": "assistant", "content": message_content})
