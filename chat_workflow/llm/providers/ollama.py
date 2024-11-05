import builtins
import sys
import os
import requests
import typing
from chainlit import logger
from datetime import datetime, timedelta
from functools import lru_cache
from inspect import signature
from typing import List, Optional, TypeVar, Dict, Any, Union
from typing import get_type_hints, get_args, get_origin
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_ollama import ChatOllama
from .base import LLMProvider

T = TypeVar('T')


class TimedCache:
    """Cache with TTL support"""

    def __init__(self, ttl_seconds: int = 300):
        self.cache = {}
        self.ttl = ttl_seconds

    def get(self, key: str) -> Optional[T]:
        if key in self.cache:
            value, timestamp = self.cache[key]
            if datetime.now() - timestamp < timedelta(seconds=self.ttl):
                return value
            del self.cache[key]
        return None

    def set(self, key: str, value: T) -> None:
        self.cache[key] = (value, datetime.now())


# 5 minute TTL for model list
model_cache = TimedCache(ttl_seconds=300)


class OllamaProvider(LLMProvider):
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url

    def create_model(self, name: str, model: str, tools: Optional[List] = None, **kwargs) -> BaseChatModel:
        # Fetch the model parameters from the Ollama API
        base_url = os.getenv("OLLAMA_URL")
        response = requests.post(
            f"{base_url}/api/show", json={"name": model})
        logger.debug(f"Response: {response}")
        params_kwargs = {}
        if response.status_code == 200:
            response_json = response.json()
            if "parameters" in response_json:
                params_kwargs = self.parse_ollama_params(
                    response_json["parameters"])

        # Merge the parameters from the Ollama API response with the provided kwargs
        # When conflict, kwargs overrides
        params_kwargs.update(kwargs)
        logger.debug(f"Params kwargs: {params_kwargs}")
        llm = ChatOllama(name=name, model=model,
                         base_url=os.getenv("OLLAMA_URL", "http://localhost:11434"), **params_kwargs)
        return llm.bind_tools(tools) if tools else llm

    def list_models(self) -> List[str]:
        cache_key = f"models_{self.base_url}"
        cached_models = model_cache.get(cache_key)
        if cached_models is not None:
            return cached_models

        try:
            response = requests.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            models = [f'{model["name"]}' for model in response.json()[
                "models"]]
            model_cache.set(cache_key, models)
            return models
        except:
            return []

    @lru_cache(maxsize=1)
    def get_ollama_param_types(self) -> Dict[str, Any]:
        """
        Dynamically extract and cache parameter types from ChatOllama
        """

        # Get all modules from langchain packages
        localns = {}
        for module_name, module in sys.modules.items():
            if module_name.startswith(('langchain', 'typing')):
                if module:
                    localns.update({
                        k: v for k, v in module.__dict__.items()
                        if isinstance(v, type) or hasattr(v, '__origin__')
                    })

        # Add built-in types
        localns.update({
            k: v for k, v in builtins.__dict__.items()
            if isinstance(v, type)
        })

        # Add typing constructs
        localns.update(typing.__dict__)

        sig = signature(ChatOllama)
        type_hints = get_type_hints(ChatOllama, localns=localns)

        param_types = {}
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            type_hint = type_hints.get(param_name, Any)
            param_types[param_name] = type_hint

        return param_types

    def parse_value(self, value_str: str, type_hint):
        """
        Parse the string value to the type specified by type_hint
        """
        origin = get_origin(type_hint)
        args = get_args(type_hint)

        if origin is Union:
            for arg_type in args:
                if arg_type == type(None):
                    continue
                try:
                    return self.parse_value(value_str, arg_type)
                except ValueError:
                    continue
            raise ValueError(f"Cannot parse {value_str} as {type_hint}")
        elif type_hint == int:
            return int(value_str)
        elif type_hint == float:
            return float(value_str)
        elif type_hint == str:
            # Keep the original string value without stripping special characters
            return value_str.strip('"\'')
        elif origin == list:
            # For stop tokens, preserve the exact string including brackets
            elem_type = args[0] if args else str

            if value_str.startswith('[') and value_str.endswith(']'):
                # Single element with brackets - return as is
                return [value_str.strip('"\'')]
            # Handle comma-separated list case
            elements = [elem.strip().strip('"\'')
                        for elem in value_str.split(',')]
            return [self.parse_value(elem, elem_type) for elem in elements]
        elif origin == dict:
            import json
            return json.loads(value_str)
        else:

            return value_str.strip('"\'')

    def parse_ollama_params(self, parameters: str) -> Dict[str, Any]:
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
        param_types = self.get_ollama_param_types()
        result = {}

        if not parameters or not isinstance(parameters, str):
            return result

        # First pass to collect all values for each key
        collected_values = {}
        for line in parameters.strip().split('\n'):
            parts = line.strip().split(None, 1)
            if len(parts) != 2:
                continue

            key, raw_value = parts
            value_str = raw_value.strip('"\'')
            if not value_str:
                continue

            if key not in collected_values:
                collected_values[key] = []
            collected_values[key].append(value_str)

        # Second pass to parse values with correct types
        for key, values in collected_values.items():
            type_hint = param_types.get(key, str)
            try:
                # If we have multiple values, treat as a list
                if len(values) > 1:
                    result[key] = [self.parse_value(v, str) for v in values]
                else:
                    result[key] = self.parse_value(values[0], type_hint)
            except (ValueError, TypeError) as e:
                logger.debug(
                    f"Skipping invalid parameter value for {key}: {values} ({e})")
                continue

        return result

    @property
    def name(self) -> str:
        return "ollama"
