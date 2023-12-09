from transformers import AutoModelForCausalLM, AutoTokenizer
from colorama import Fore, Style

model_name_or_path = r"E:\ai\llm_models\lmstudio\TheBloke\Llama-2-7B-Chat-GPTQ"
# To use a different branch, change revision
# For example: revision="gptq-4bit-64g-actorder_True"
model = AutoModelForCausalLM.from_pretrained(model_name_or_path,
                                             device_map="auto",
                                             trust_remote_code=False,
                                             revision="main")

tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, use_fast=True)

# Initialize the conversation history with the system's role
conversation_history = [{"role": "system", "content": "You are a helpful assistant."}]

# Start the conversation loop
while True:
    # Get user input and append it to the conversation history
    user_message = input(Fore.GREEN + "User: " + Style.RESET_ALL)
    conversation_history.append({"role": "user", "content": user_message})

    # Prepare the prompt template
    prompt_template=f'''[INST] <<SYS>>
    You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe.  Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature. If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information.
    <</SYS>>
    {user_message}[/INST]
    '''

    # Generate response
    input_ids = tokenizer(prompt_template, return_tensors='pt').input_ids.cuda()
    output = model.generate(inputs=input_ids, temperature=0.7, do_sample=True, top_p=0.95, top_k=40, max_new_tokens=512)
    response = tokenizer.decode(output[0], skip_special_tokens=True)

    # Append the response to the conversation history
    conversation_history.append({"role": "assistant", "content": response})
    print(conversation_history)
    # Print the assistant's response
    print(Fore.CYAN + "Assistant: " + Style.RESET_ALL + response)


