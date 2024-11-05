import os
from typing import List, Optional
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.chat_models import BaseChatModel
from ..base import LLMProvider


class AnthropicProvider(LLMProvider):
    def create_model(self, name: str, model: str, tools: Optional[List] = None, **kwargs) -> BaseChatModel:
        llm = ChatAnthropic(name=name, model=model, **kwargs)
        return llm.bind_tools(tools) if tools else llm

    def list_models(self) -> List[str]:
        """
        List all available Anthropic models

        Currently, the Anthropic Python module does not offer a direct API 
        endpoint to list all available Claude models.
        """
        if os.getenv("ANTHROPIC_API_KEY"):
            return [f"({self.name}){model_name}" for model_name in ["claude-3-5-haiku-20241022", "claude-3-5-sonnet-20241022"]]
        else:
            return []

    @property
    def name(self) -> str:
        return "anthropic"
