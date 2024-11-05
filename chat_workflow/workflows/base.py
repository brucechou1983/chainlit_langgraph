import operator
import chainlit as cl
from typing import TypedDict, Annotated, Sequence, Dict, Optional
from langchain_core.messages import AnyMessage, HumanMessage
from abc import ABC, abstractmethod
from typing import Dict, Any
from langgraph.graph import StateGraph, END


class BaseState(TypedDict):
    # Message history
    messages: Annotated[Sequence[AnyMessage], operator.add]

    # Name of the workflow
    chat_profile: str


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

    @classmethod
    @abstractmethod
    def name(cls) -> str:
        pass

    @property
    @abstractmethod
    def output_chat_model(self) -> str:
        """
        The name of the chat model to display in the UI. 
        Normally, this is the name of the chat model that is 
        used to generate the final output.
        """

    @classmethod
    @abstractmethod
    def chat_profile(cls) -> cl.ChatProfile:
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

    def tool_routing(self, state: BaseState):
        """
        Use in the conditional_edge to route to the ToolNode if the last message
        has tool calls. Otherwise, route to the end.
        """
        if isinstance(state, list):
            ai_message = state[-1]
        elif messages := state.get("messages", []):
            ai_message = messages[-1]
        else:
            raise ValueError(
                f"No messages found in input state to tool_edge: {state}")
        if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
            return "tools"
        return END

    async def get_chat_settings(self, state: Optional[BaseState] = None) -> cl.ChatSettings:
        """
        Get the chat settings for the workflow.

        Args:
            state (Optional[BaseState]): The state of the workflow. Used to resume a chat from previous session.
        """
        settings = self.chat_settings
        # Resume settings from previous session
        if state is not None:
            for widget in settings.inputs:
                if widget.id in state:
                    if isinstance(widget, cl.input_widget.Select):
                        if widget.items:
                            if state[widget.id] in widget.items.values():
                                widget.initial = state[widget.id]
                        elif widget.values:
                            if state[widget.id] in widget.values:
                                widget.initial = state[widget.id]
                    elif isinstance(widget, cl.input_widget.Switch):
                        widget.initial = state[widget.id]
                    elif isinstance(widget, cl.input_widget.Slider):
                        if widget.min > state[widget.id]:
                            widget.initial = widget.min
                        elif widget.max < state[widget.id]:
                            widget.initial = widget.max
                        else:
                            widget.initial = state[widget.id]
                    elif isinstance(widget, cl.input_widget.TextInput):
                        widget.initial = state[widget.id]
                    elif isinstance(widget, cl.input_widget.NumberInput):
                        widget.initial = state[widget.id]
                    elif isinstance(widget, cl.input_widget.Tags):
                        if widget.values:
                            widget.initial = [
                                tag for tag in state[widget.id] if tag in widget.values]
                        else:
                            widget.initial = state[widget.id]
        return await settings.send()

    def format_message(self, message: cl.Message) -> HumanMessage:
        return HumanMessage(content=message.content)
