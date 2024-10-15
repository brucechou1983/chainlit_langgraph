import operator
from typing import TypedDict, Annotated, Sequence, Dict
from langchain_core.messages import AnyMessage
from abc import ABC, abstractmethod
from typing import Dict, Any
from langgraph.graph import StateGraph


class BaseWorkflow(ABC):
    @abstractmethod
    def create_graph(self) -> StateGraph:
        pass

    @abstractmethod
    def create_default_state(self) -> Dict[str, Any]:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def output_chat_model(self) -> str:
        pass


class BaseState(TypedDict):
    # Message history
    messages: Annotated[Sequence[AnyMessage], operator.add]
