import os
import re
from dotenv import load_dotenv
from typing import Optional, List
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from .openai import list_openai_models
from .anthropic import list_anthropic_models
from .ollama import create_chat_ollama_model, list_ollama_models

load_dotenv()


def create_chat_model(name: str, model: str, tools: Optional[List] = None, **kwargs) -> BaseChatModel:
    if re.match(r"^claude-*", model):
        llm = ChatAnthropic(name=name, model=model, **kwargs)
    elif re.match(r"^gpt-*", model):
        llm = ChatOpenAI(name=name, model=model, **kwargs)
    elif match := re.match(r"^\(ollama\)(.*)", model):
        "ex: '(ollama)llama3.2' -> 'llama3.2'"
        model_name = match.group(1)
        return create_chat_ollama_model(name, model_name, **kwargs)

    if tools is None:
        return llm
    else:
        return llm.bind_tools(tools)


def list_available_llm() -> List[str]:
    """
    List all available models
    """
    return list_ollama_models(os.getenv("OLLAMA_URL", "http://localhost:11434")) + list_openai_models() + list_anthropic_models()
