import os
from openai import OpenAI
from typing import List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel
from .base import LLMProvider


class XAIProvider(LLMProvider):
    def create_model(self, name: str, model: str, tools: Optional[List] = None, **kwargs) -> BaseChatModel:
        llm = ChatOpenAI(
            name=name,
            model=model,
            api_key=os.getenv("XAI_API_KEY"),
            base_url=os.getenv("XAI_BASE_URL"),
            **kwargs
        )
        return llm.bind_tools(tools) if tools else llm

    def list_models(self) -> List[str]:
        """
        List all available XAI models

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
            client = OpenAI(api_key=os.getenv("XAI_API_KEY"),
                            base_url=os.getenv("XAI_BASE_URL"))
            response = client.models.list()
            return [f'{model.id}' for model in response.data]
        except Exception as e:
            return []

    @property
    def name(self) -> str:
        return "xai"
