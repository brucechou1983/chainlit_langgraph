from abc import ABC, abstractmethod
from typing import List, Optional
from langchain_core.language_models.chat_models import BaseChatModel


class LLMProvider(ABC):
    @abstractmethod
    def create_model(self, name: str, model: str, tools: Optional[List] = None, **kwargs) -> BaseChatModel:
        pass

    @abstractmethod
    def list_models(self) -> List[str]:
        pass

    @property
    def name(self) -> str:
        raise NotImplementedError
