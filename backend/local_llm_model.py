"""using llms other than openai"""
import os
from dotenv import load_dotenv
import google.generativeai as palm
from llama_index.llms.palm import PaLM
from llama_index.core import Settings


load_dotenv()
palm_api_key = os.getenv("GOOGLE_API_KEY")
palm.configure(api_key=palm_api_key)

def completion_to_prompt(completion):
    """customizing prompt"""
    return f"<|system|>\n</s>\n<|user|>\n{completion}</s>\n<|assistant|>\n"


def messages_to_prompt(messages):
    """customizing chat prompt"""
    prompt = ""
    for message in messages:
        if message.role == "system":
            prompt += f"<|system|>\n{message.content}</s>\n"
        elif message.role == "user":
            prompt += f"<|user|>\n{message.content}</s>\n"
        elif message.role == "assistant":
            prompt += f"<|assistant|>\n{message.content}</s>\n"

    # ensure we start with a system prompt, insert blank if needed
    if not prompt.startswith("<|system|>\n"):
        prompt = "<|system|>\n</s>\n" + prompt

    # add final assistant prompt
    prompt = prompt + "<|assistant|>\n"

    return prompt


def load_local_llm():
    """returns gemini pro llm model"""
    local_llm_model = PaLM(
        model="gemini-pro",
        api_key=palm_api_key,
        messages_to_prompt= messages_to_prompt,
        completion_to_prompt=completion_to_prompt
    )
    Settings.llm = local_llm_model
    return local_llm_model
