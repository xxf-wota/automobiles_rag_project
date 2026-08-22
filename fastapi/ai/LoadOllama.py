import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama

load_dotenv()
def load_ollama() -> ChatOllama:
    return ChatOllama(
        model=os.getenv("OLLAMA_MODEL_NAME"),
        base_url=os.getenv("OLLAMA_BASE_URL"),
    )