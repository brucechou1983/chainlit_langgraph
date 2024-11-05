from typing import Dict, Optional, List
from langchain_core.language_models.chat_models import BaseChatModel
from .base import LLMProvider


class LLMFactory:
    def __init__(self):
        self._providers: Dict[str, LLMProvider] = {}

    def register_provider(self, prefix: str, provider: LLMProvider):
        self._providers[prefix] = provider

    def create_model(self, name: str, model: str, tools: Optional[List] = None, **kwargs) -> BaseChatModel:
        for provider_name, provider in self._providers.items():
            prefix = f"({provider_name})"
            if model.startswith(prefix):
                model_name = model.replace(prefix, "")
                return provider.create_model(name, model_name, tools, **kwargs)
        raise ValueError(f"No provider found for model: {model}")

    def list_available_models(self) -> List[str]:
        models = []
        for provider in self._providers.values():
            models.extend(provider.list_models())
        return models
