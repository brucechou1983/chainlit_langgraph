import os
from chainlit import logger
from openai import OpenAI
from typing import List, Optional, Dict, Set
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models.chat_models import BaseChatModel
from .base import LLMProvider
from ..capabilities import ModelCapability


class GoogleProvider(LLMProvider):
    def create_model(self, name: str, model: str, tools: Optional[List] = None, **kwargs) -> BaseChatModel:
        llm = ChatGoogleGenerativeAI(
            name=name,
            model=model,
            max_tokens=None,
            **kwargs
        )
        return llm.bind_tools(tools) if tools else llm

    def list_models(self) -> List[str]:
        return ["gemini-1.5-pro", "gemini-1.5-flash"]

    @property
    def name(self) -> str:
        return "google"

    @property
    def capabilities(self) -> Dict[str, Set[ModelCapability]]:
        return {
            "gemini-1.5-pro": {ModelCapability.TEXT_TO_TEXT, ModelCapability.IMAGE_TO_TEXT, ModelCapability.TOOL_CALLING},
            "gemini-1.5-flash": {ModelCapability.TEXT_TO_TEXT, ModelCapability.IMAGE_TO_TEXT, ModelCapability.TOOL_CALLING},
        }
