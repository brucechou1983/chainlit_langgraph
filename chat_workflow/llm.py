from typing import Dict, Union, List
import os
import re
import requests
from chainlit import logger
from dotenv import load_dotenv
from openai import OpenAI
from typing import Optional, List
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

load_dotenv()


# Ollama parameter type definitions
OLLAMA_INT_PARAMS = {
    'mirostat', 'num_ctx', 'num_gpu', 'num_thread',
    'num_predict', 'repeat_last_n', 'top_k', 'seed'
}
OLLAMA_FLOAT_PARAMS = {
    'mirostat_eta', 'mirostat_tau', 'repeat_penalty',
    'temperature', 'tfs_z', 'top_p'
}
OLLAMA_LIST_PARAMS = {'stop'}
OLLAMA_STR_PARAMS = {
    'format',  # Can be "" or "json"
    'base_url',
    'keep_alive',  # Can be int or str
    'model'
}


def _parse_ollama_params(parameters: str) -> Dict[str, Union[int, float, List[str], str]]:
    """
    Parse the parameters from the Ollama API response

    Args:
        parameters: Raw parameter string from Ollama API

    Returns:
        Dict of parsed parameters with appropriate types

    Example:
        Input: 'num_ctx                        4096\nstop                           "[INST]"\nstop                           "[/INST]"'
        Output: {
            "num_ctx": 4096,
            "stop": ["[INST]", "[/INST]"]
        }
    """
    result = {}
    if not parameters or not isinstance(parameters, str):
        return result

    for line in parameters.strip().split('\n'):
        parts = line.strip().split(None, 1)
        if len(parts) != 2:
            continue

        key, raw_value = parts
        value = raw_value.strip('"\'')
        if not value:
            continue

        try:
            if key in OLLAMA_LIST_PARAMS:
                if key not in result:
                    result[key] = []
                result[key].append(value)
            elif key in OLLAMA_INT_PARAMS:
                result[key] = int(value)
            elif key in OLLAMA_FLOAT_PARAMS:
                result[key] = float(value)
            elif key in OLLAMA_STR_PARAMS:
                # Special handling for keep_alive which can be int or str
                if key == 'keep_alive':
                    try:
                        result[key] = int(value)
                    except ValueError:
                        result[key] = value
                else:
                    result[key] = value
        except (ValueError, TypeError):
            logger.debug(
                f"Skipping invalid parameter value: {key}={raw_value}")
            continue

    return result


def _create_chat_ollama_model(name: str, model: str, **kwargs) -> BaseChatModel:
    # Fetch the model parameters from the Ollama API
    base_url = os.getenv("OLLAMA_URL")
    response = requests.post(
        f"{base_url}/api/show", json={"name": model})
    logger.debug(f"Response: {response}")
    params_kwargs = {}
    if response.status_code == 200:
        response_json = response.json()
        if "parameters" in response_json:
            params_kwargs = _parse_ollama_params(response_json["parameters"])

    # Merge the parameters from the Ollama API response with the provided kwargs
    # When conflict, kwargs overrides
    params_kwargs.update(kwargs)
    logger.debug(f"Params kwargs: {params_kwargs}")
    return ChatOllama(name=name, model=model,
                      base_url=os.getenv("OLLAMA_URL", "http://localhost:11434"), **params_kwargs)


def create_chat_model(name: str, model: str, tools: Optional[List] = None, **kwargs) -> BaseChatModel:
    if re.match(r"^claude-*", model):
        llm = ChatAnthropic(name=name, model=model, **kwargs)
    elif re.match(r"^gpt-*", model):
        llm = ChatOpenAI(name=name, model=model, **kwargs)
    elif match := re.match(r"^\(ollama\)(.*)", model):
        "ex: '(ollama)llama3.2' -> 'llama3.2'"
        model_name = match.group(1)
        return _create_chat_ollama_model(name, model_name, **kwargs)

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
        return [f'(ollama){model["name"]}' for model in response.json()["models"]]
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
