import os
import requests
from typing import List, Optional, Dict, Set
from langchain_groq import ChatGroq
from langchain_core.language_models.chat_models import BaseChatModel
from .base import LLMProvider
from ..capabilities import ModelCapability


class GroqProvider(LLMProvider):
    def create_model(self, name: str, model: str, tools: Optional[List] = None, **kwargs) -> BaseChatModel:
        llm = ChatGroq(name=name, model=model, **kwargs)
        return llm.bind_tools(tools) if tools else llm

    def list_models(self) -> List[str]:
        api_key = os.environ.get("GROQ_API_KEY")
        url = "https://api.groq.com/openai/v1/models"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers)
        models_data = response.json()
        return [model["id"] for model in models_data["data"]]

    @property
    def name(self) -> str:
        return "groq"

    @property
    def capabilities(self) -> Dict[str, Set[ModelCapability]]:
        return {
            "llama-3.2-3b-preview": {ModelCapability.TEXT_TO_TEXT, ModelCapability.TOOL_CALLING},
            "llama-3.2-11b-vision-preview": {ModelCapability.TEXT_TO_TEXT, ModelCapability.IMAGE_TO_TEXT, ModelCapability.TOOL_CALLING},
            "llama-3.2-90b-vision-preview": {ModelCapability.TEXT_TO_TEXT, ModelCapability.IMAGE_TO_TEXT, ModelCapability.TOOL_CALLING},
            "whisper-large-v3": {ModelCapability.AUDIO_TO_TEXT},
        }
