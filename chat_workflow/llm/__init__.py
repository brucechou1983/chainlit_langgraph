import os
from typing import List, Optional
from langchain_core.language_models.chat_models import BaseChatModel
from .factory import LLMFactory
from .providers import OllamaProvider, OpenAIProvider, AnthropicProvider, XAIProvider

# Initialize factory
llm_factory = LLMFactory()
# Register providers
llm_factory.register_provider(
    "ollama", OllamaProvider(os.getenv("OLLAMA_URL")))
llm_factory.register_provider("openai", OpenAIProvider())
llm_factory.register_provider("anthropic", AnthropicProvider())
llm_factory.register_provider("xai", XAIProvider())


def create_chat_model(name: str, model: str, tools: Optional[List] = None, **kwargs) -> BaseChatModel:
    return llm_factory.create_model(name, model, tools, **kwargs)


def list_available_llm() -> List[str]:
    return llm_factory.list_available_models()
