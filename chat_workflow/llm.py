import re
from typing import Optional, List
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI


def _create_chat_ollama_model(name: str, model: str, **kwargs) -> BaseChatModel:
    stop = None
    if model in ["llama3, llama3.1, llama3.2"]:
        stop = [
            "<|start_header_id|>",
            "<|end_header_id|>",
            "<|eot_id|>",
            "<|reserved_special_token"
        ]

    return ChatOllama(name=name, model=model, stop=stop, **kwargs)


def create_chat_model(name: str, model: str, tools: Optional[List] = None, **kwargs) -> BaseChatModel:
    if re.match(r"^claude-*", model):
        extra_headers = {
            "anthropic-beta": "prompt-caching-2024-07-31"
        }
        llm = ChatAnthropic(name=name, model=model,
                            extra_headers=extra_headers, **kwargs)
        # llm = ChatAnthropic(name=name, model=model, **kwargs)
    elif re.match(r"^gpt-*", model):
        llm = ChatOpenAI(name=name, model=model, **kwargs)
    elif match := re.match(r"^ollama-(.*)", model):
        "ex: 'ollama-llama3.2' -> 'llama3.2'"
        model_name = match.group(1)
        return _create_chat_ollama_model(name, model_name, **kwargs)
    else:
        raise ValueError(f"Unsupported chat model: {model}")

    if tools is None:
        return llm
    else:
        return llm.bind_tools(tools)
