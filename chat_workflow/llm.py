import os
import re
import requests
from dotenv import load_dotenv
from openai import OpenAI
from typing import Optional, List
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

load_dotenv()


def _create_chat_ollama_model(name: str, model: str, **kwargs) -> BaseChatModel:
    stop = None
    if model in ["llama3, llama3.1, llama3.2", "llama3.2:3b-instruct-q8_0"]:
        stop = [
            "<|start_header_id|>",
            "<|end_header_id|>",
            "<|eot_id|>"
        ]
    return ChatOllama(name=name, model=model, stop=stop,
                      base_url=os.getenv("OLLAMA_URL", "http://localhost:11434"), **kwargs)


def create_chat_model(name: str, model: str, tools: Optional[List] = None, **kwargs) -> BaseChatModel:
    if re.match(r"^claude-*", model):
        llm = ChatAnthropic(name=name, model=model, **kwargs)
    elif re.match(r"^gpt-*", model):
        llm = ChatOpenAI(name=name, model=model, **kwargs)
    elif match := re.match(r"^ollama-(.*)", model):
        "ex: 'ollama-llama3.2' -> 'llama3.2'"
        model_name = match.group(1)
        llm = _create_chat_ollama_model(name, model_name, **kwargs)
    else:
        raise ValueError(f"Unsupported chat model: {model}")

    if tools is None:
        return llm
    else:
        return llm.bind_tools(tools)


# List all available Ollama models by hitting the api endpoint
# api endpoint: curl http://localhost:11434/api/tags
# api response sample:
# {
#   "models": [
#     {
#       "name": "codellama:13b",
#       "modified_at": "2023-11-04T14:56:49.277302595-07:00",
#       "size": 7365960935,
#       "digest": "9f438cb9cd581fc025612d27f7c1a6669ff83a8bb0ed86c94fcf4c5440555697",
#       "details": {
#         "format": "gguf",
#         "family": "llama",
#         "families": null,
#         "parameter_size": "13B",
#         "quantization_level": "Q4_0"
#       }
#     },
#     {
#       "name": "llama3:latest",
#       "modified_at": "2023-12-07T09:32:18.757212583-08:00",
#       "size": 3825819519,
#       "digest": "fe938a131f40e6f6d40083c9f0f430a515233eb2edaa6d72eb85c50d64f2300e",
#       "details": {
#         "format": "gguf",
#         "family": "llama",
#         "families": null,
#         "parameter_size": "7B",
#         "quantization_level": "Q4_0"
#       }
#     }
#   ]
# }
# when no model is available or an exception, just return an empty list
def list_ollama_models(url: str = "http://localhost:11434") -> List[str]:
    """
    List all available Ollama models by hitting the api endpoint

    Args:
        url (str): The url of the Ollama API endpoint
    """
    try:
        response = requests.get(f"{url}/api/tags")
        response.raise_for_status()
        return [f'ollama-{model["name"]}' for model in response.json()["models"]]
    except:
        return []

# List all openai models


def list_openai_models() -> List[str]:
    """
    List all available OpenAI models

    Sample Response:
    {
      "object": "list",
      "data": [
        {
          "id": "model-id-0",
          "object": "model",
          "created": 1686935002,
          "owned_by": "organization-owner"
        },
        {
          "id": "model-id-1",
          "object": "model",
          "created": 1686935002,
          "owned_by": "organization-owner",
        },
        {
          "id": "model-id-2",
          "object": "model",
          "created": 1686935002,
          "owned_by": "openai"
        },
      ],
      "object": "list"
    }
    """
    try:
        client = OpenAI()
        response = client.models.list()
        # Only use model id starting with "gpt-4o-"
        return [f'{model.id}' for model in response.data if model.id.startswith("gpt-4o-")]
    except Exception as e:
        return []


def list_anthropic_models() -> List[str]:
    """
    List all available Anthropic models

    Currently, the Anthropic Python module does not offer a direct API 
    endpoint to list all available Claude models.
    """
    if os.getenv("ANTHROPIC_API_KEY"):
        return ["claude-3-haiku-20240307", "claude-3-5-sonnet-20241022"]
    else:
        return []


def list_available_llm() -> List[str]:
    """
    List all available models
    """
    return list_ollama_models(os.getenv("OLLAMA_URL", "http://localhost:11434")) + list_openai_models() + list_anthropic_models()
