from typing import Dict, Optional, List
from langchain_core.language_models.chat_models import BaseChatModel
from .providers.base import LLMProvider
from .capabilities import ModelCapability


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
                if ModelCapability.TOOL_CALLING in provider.capabilities.get(model_name, set()):
                    return provider.create_model(name, model_name, tools, **kwargs)
                else:
                    if tools is not None:
                        raise ValueError(
                            f"Model {model_name} does not support tool calling")
                    return provider.create_model(name, model_name, **kwargs)
        raise ValueError(f"No provider found for model: {model}")

    def list_models(self, capabilities: Optional[set[ModelCapability]] = None) -> List[str]:
        models = []
        for provider in self._providers.values():
            provider_models = provider.list_models()
            if capabilities:
                models.extend([f"({provider.name}){model_name}" for model_name in provider_models
                               if all(cap in provider.capabilities.get(model_name, set()) for cap in capabilities)])
            else:
                models.extend(
                    [f"({provider.name}){model_name}" for model_name in provider_models])
        return models
