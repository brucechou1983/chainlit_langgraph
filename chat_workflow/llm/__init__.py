import os
from typing import List, Optional
from langchain_core.language_models.chat_models import BaseChatModel
from .factory import LLMFactory
from .capabilities import ModelCapability  # noqa
from .providers import OllamaProvider, OpenAIProvider, AnthropicProvider, XAIProvider, GroqProvider, GoogleProvider

# Initialize factory
llm_factory = LLMFactory()
# Register providers
llm_factory.register_provider(
    "ollama", OllamaProvider(os.getenv("OLLAMA_URL")))
llm_factory.register_provider("openai", OpenAIProvider())
llm_factory.register_provider("anthropic", AnthropicProvider())
llm_factory.register_provider("xai", XAIProvider())
llm_factory.register_provider("groq", GroqProvider())
llm_factory.register_provider("google", GoogleProvider())
