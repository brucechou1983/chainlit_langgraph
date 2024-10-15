import os
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable, RunnableConfig
from .base import BaseWorkflow, ChatState
from ..llm import create_chat_model
from ..tools import BasicToolNode
from ..tools.search import search
from ..tools.time import get_datetime_now


class GraphState(ChatState):
    name: str


class SimpleChatWorkflow(BaseWorkflow):
    def __init__(self):
        super().__init__()
        self.tools = [get_datetime_now]

    def enrich_tools(self):
        # TODO: check if tools are valid
        self.tools.append(search)

    def create_graph(self) -> StateGraph:
        self.enrich_tools()

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
            "chat_model", model=state["chat_model"], tools=self.tools)
        chain: Runnable = prompt | llm
        print(f"llm: {llm}")
        return {
            "messages": [await chain.ainvoke(state, config=config)]
        }

    def create_default_state(self) -> GraphState:
        return {
            "name": "simple_chat",
            "messages": [],
            "chat_model": os.getenv("CHAT_MODEL", "ollama-llama3.2"),
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
        return "simple_chat"
