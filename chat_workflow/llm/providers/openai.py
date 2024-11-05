from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from openai import OpenAI
from typing import Optional, List
from .base import LLMProvider


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
            # Only use model id starting with "gpt-4o-"
            return [f'{model.id}' for model in response.data if model.id.startswith("gpt-4o-")]
        except Exception as e:
            return []

    @property
    def name(self) -> str:
        return "openai"
