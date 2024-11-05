from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from openai import OpenAI
from typing import Optional, List, Dict, Set
from .base import LLMProvider
from ..capabilities import ModelCapability


class OpenAIProvider(LLMProvider):
    def create_model(self, name: str, model: str, tools: Optional[List] = None, **kwargs) -> BaseChatModel:
        llm = ChatOpenAI(name=name, model=model, **kwargs)
        return llm.bind_tools(tools) if tools else llm

    def list_models(self) -> List[str]:
        """
        List all available OpenAI models

        Sample Response:
        {
          "object": "list",
          "data": [
            {
              "id": "model-id-0",
              "object": "model",
              "created": 1686935002,
              "owned_by": "organization-owner"
            },
            {
              "id": "model-id-1",
              "object": "model",
              "created": 1686935002,
              "owned_by": "organization-owner",
            },
            {
              "id": "model-id-2",
              "object": "model",
              "created": 1686935002,
              "owned_by": "openai"
            },
          ],
          "object": "list"
        }
        """
        try:
            client = OpenAI()
            response = client.models.list()
            return [f'{model.id}' for model in response.data]
        except Exception as e:
            return []

    @property
    def name(self) -> str:
        return "openai"

    @property
    def capabilities(self) -> Dict[str, Set[ModelCapability]]:
        return {
            "gpt-4o": {ModelCapability.TEXT_TO_TEXT, ModelCapability.IMAGE_TO_TEXT, ModelCapability.TOOL_CALLING, ModelCapability.STRUCTURED_OUTPUT},
            "gpt-4o-mini": {ModelCapability.TEXT_TO_TEXT, ModelCapability.IMAGE_TO_TEXT, ModelCapability.TOOL_CALLING, ModelCapability.STRUCTURED_OUTPUT},
            "gpt-4o-audio-preview": {ModelCapability.TEXT_TO_TEXT, ModelCapability.IMAGE_TO_TEXT, ModelCapability.TOOL_CALLING, ModelCapability.STRUCTURED_OUTPUT, ModelCapability.AUDIO_TO_TEXT, ModelCapability.TEXT_TO_AUDIO},
            # "gpt-4o-realtime": {ModelCapability.TEXT_TO_TEXT, ModelCapability.IMAGE_TO_TEXT, ModelCapability.TOOL_CALLING, ModelCapability.STRUCTURED_OUTPUT, ModelCapability.AUDIO_TO_TEXT, ModelCapability.TEXT_TO_AUDIO},
            "text-embedding-3-large": {ModelCapability.TEXT_EMBEDDING},
            "text-embedding-3-small": {ModelCapability.TEXT_EMBEDDING},
            "tts-1": {ModelCapability.TEXT_TO_AUDIO},
            "whisper-1": {ModelCapability.AUDIO_TO_TEXT},
            "dalle-3": {ModelCapability.TEXT_TO_IMAGE},
        }
