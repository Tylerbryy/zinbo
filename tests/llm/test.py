# Fixed code with proper handling of the conversation history and response appending
from llama_cpp import Llama
from colorama import Fore, Style

# Initialize the Llama model with the specified parameters
llm = Llama(model_path=r"E:\ai\llm_models\open-hermes-2.5-mistral\openhermes-2.5-mistral-7b.Q5_K_S.gguf", 
            chat_format="chatml", n_gpu_layers=50, n_ctx=3584, n_batch=512)

# Initialize the conversation history with the system's role
conversation_history = [{"role": "system", "content": "You are a helpful assistant named Nova."}]

# Start the conversation loop
while True:
    # Get user input and append it to the conversation history
    user_message = input(Fore.GREEN + "User: " + Style.RESET_ALL)
    conversation_history.append({"role": "user", "content": user_message})
    
    # Generate a response from the Llama model
    response = llm.create_chat_completion(messages=conversation_history)
    
    # Extract the message content from the response
    message_content = response["choices"][0]["message"]["content"].replace("[INST]", "").replace("<<SYS>>", "").replace("</SYS>", "").replace("<</A>", "").replace("<@A>", "").replace("[/INST]", "").strip()
    
    
    # Print the model's response
    print(Fore.CYAN + "Nova: " + Style.RESET_ALL + message_content)
    
    # Append the model's response to the conversation history
    conversation_history.append({"role": "assistant", "content": message_content})