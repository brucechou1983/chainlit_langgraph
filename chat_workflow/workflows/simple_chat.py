import chainlit as cl
from chainlit.input_widget import Select
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable, RunnableConfig
from .base import BaseWorkflow, BaseState
from ..llm import create_chat_model, list_available_llm
from ..tools import BasicToolNode
from ..tools.search import search
from ..tools.time import get_datetime_now


class GraphState(BaseState):
    # Model name of the chatbot
    chat_model: str


class SimpleChatWorkflow(BaseWorkflow):
    def __init__(self):
        super().__init__()

        # TODO: check tool availability
        self.tools = [get_datetime_now, search]

    def create_graph(self) -> StateGraph:
        graph = StateGraph(GraphState)
        graph.add_node("chat", self.chat_node)
        graph.add_node("tools", BasicToolNode(self.tools))

        # TODO: create a router for using multiple tools
        graph.set_entry_point("chat")
        graph.add_conditional_edges("chat", self.tool_routing)
        graph.add_edge("tools", "chat")
        return graph

    async def chat_node(self, state: GraphState, config: RunnableConfig) -> GraphState:
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="You're a helpful assistant."),
            MessagesPlaceholder(variable_name="messages"),
        ])
        llm = create_chat_model(
            self.output_chat_model, model=state["chat_model"], tools=self.tools)
        chain: Runnable = prompt | llm
        return {
            "messages": [await chain.ainvoke(state, config=config)]
        }

    def create_default_state(self) -> GraphState:
        return {
            "name": self.name,
            "messages": [],
            "chat_model": "",
        }

    def tool_routing(self, state: GraphState):
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

    @property
    def name(self) -> str:
        return "Simple Chat"

    @property
    def output_chat_model(self) -> str:
        return "chat_model"

    @property
    def chat_profile(self) -> cl.ChatProfile:
        return cl.ChatProfile(
            name=self.name,
            markdown_description="A ChatGPT-like chatbot.",
            icon="https://picsum.photos/150",
            default=True,
            # starters=[
            #     cl.Starter(
            #         label="Programming",
            #         message="Write a snake game in Python.",
            #     ),
        )

    @property
    def chat_settings(self) -> cl.ChatSettings:
        return cl.ChatSettings([
            Select(
                id="chat_model",
                label="Chat Model",
                values=sorted(list_available_llm()),
                initial_index=0,
            ),
        ])
