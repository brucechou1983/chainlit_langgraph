import os
from typing import List, Optional, Dict, Set
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.chat_models import BaseChatModel
from .base import LLMProvider
from ..capabilities import ModelCapability


class AnthropicProvider(LLMProvider):
    def create_model(self, name: str, model: str, tools: Optional[List] = None, **kwargs) -> BaseChatModel:
        llm = ChatAnthropic(name=name, model=model, **kwargs)
        if tools and len(tools) > 0 and ModelCapability.TOOL_CALLING in self.capabilities.get(model, set()):
            return llm.bind_tools(tools)
        return llm

    def list_models(self) -> List[str]:
        """
        List all available Anthropic models

        Currently, the Anthropic Python module does not offer a direct API 
        endpoint to list all available Claude models.
        """
        if os.getenv("ANTHROPIC_API_KEY"):
            return self.capabilities.keys()
        else:
            return []

    @property
    def name(self) -> str:
        return "anthropic"

    @property
    def capabilities(self) -> Dict[str, Set[ModelCapability]]:
        return {
            "claude-3-5-haiku-20241022": {ModelCapability.TEXT_TO_TEXT, ModelCapability.TOOL_CALLING, ModelCapability.STRUCTURED_OUTPUT},
            "claude-3-5-sonnet-20241022": {ModelCapability.TEXT_TO_TEXT, ModelCapability.IMAGE_TO_TEXT, ModelCapability.TOOL_CALLING, ModelCapability.STRUCTURED_OUTPUT},
        }
