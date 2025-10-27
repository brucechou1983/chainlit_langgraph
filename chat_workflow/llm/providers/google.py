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
        return [
            "gemini-2.5-pro",
            "gemini-2.5-flash",
            "gemini-2.5-flash-preview-09-2025",
            "gemini-2.5-flash-lite",
            "gemini-2.5-flash-image",
        ]

    @property
    def name(self) -> str:
        return "google"

    @property
    def capabilities(self) -> Dict[str, Set[ModelCapability]]:
        return {
            "gemini-2.5-pro": {ModelCapability.TEXT_TO_TEXT, ModelCapability.IMAGE_TO_TEXT, ModelCapability.TOOL_CALLING},
            "gemini-2.5-flash": {ModelCapability.TEXT_TO_TEXT, ModelCapability.IMAGE_TO_TEXT, ModelCapability.TOOL_CALLING},
            "gemini-2.5-flash-preview-09-2025": {ModelCapability.TEXT_TO_TEXT, ModelCapability.IMAGE_TO_TEXT, ModelCapability.TOOL_CALLING},
            "gemini-2.5-flash-lite": {ModelCapability.TEXT_TO_TEXT, ModelCapability.IMAGE_TO_TEXT, ModelCapability.TOOL_CALLING},
            "gemini-2.5-flash-image": {ModelCapability.TEXT_TO_TEXT, ModelCapability.IMAGE_TO_TEXT, ModelCapability.TEXT_TO_IMAGE, ModelCapability.TOOL_CALLING},
        }
