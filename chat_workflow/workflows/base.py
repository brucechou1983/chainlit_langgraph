import operator
import chainlit as cl
from typing import TypedDict, Annotated, Sequence, Dict
from langchain_core.messages import AnyMessage
from abc import ABC, abstractmethod
from typing import Dict, Any
from langgraph.graph import StateGraph


class BaseWorkflow(ABC):
    @abstractmethod
    def create_graph(self) -> StateGraph:
        """
        Define the state graph of the workflow.
        """

    @abstractmethod
    def create_default_state(self) -> Dict[str, Any]:
        """
        Define the default state of the workflow.
        """

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def output_chat_model(self) -> str:
        """
        The name of the chat model to display in the UI. 
        Normally, this is the name of the chat model that is 
        used to generate the final output.
        """

    @property
    @abstractmethod
    def chat_profile(self) -> cl.ChatProfile:
        """
        Chat profile to display in the UI. This is for providing
        an option in the list of available workflows to the user.
        """

    @property
    @abstractmethod
    def chat_settings(self) -> cl.ChatSettings:
        """
        Chatt settings to display in the UI. This is for providing
        customizable settings to the user.
        """

    async def get_chat_settings(self) -> cl.ChatSettings:
        """
        Get the chat settings for the workflow.
        """
        return await self.chat_settings.send()


class BaseState(TypedDict):
    # Message history
    messages: Annotated[Sequence[AnyMessage], operator.add]
