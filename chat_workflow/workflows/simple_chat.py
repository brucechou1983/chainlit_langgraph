import chainlit as cl
from chainlit.input_widget import Select, TextInput
from langgraph.graph import StateGraph
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable, RunnableConfig
from .base import BaseWorkflow, BaseState
from ..llm import llm_factory, ModelCapability
from ..tools import BasicToolNode
from ..tools.search import get_search_tools
from ..tools.time import get_datetime_now


class GraphState(BaseState):
    # Model name of the chatbot
    chat_model: str

    # System Prompt
    chat_system_prompt: str


class SimpleChatWorkflow(BaseWorkflow):
    def __init__(self):
        super().__init__()

        self.capabilities = {
            ModelCapability.TEXT_TO_TEXT, ModelCapability.TOOL_CALLING}
        self.tools = [get_datetime_now] + get_search_tools()

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
            SystemMessage(content=state["chat_system_prompt"]),
            MessagesPlaceholder(variable_name="messages"),
        ])
        llm = llm_factory.create_model(
            self.output_chat_model, model=state["chat_model"], tools=self.tools)
        chain: Runnable = prompt | llm
        return {
            "messages": [await chain.ainvoke(state, config=config)]
        }

    def create_default_state(self) -> GraphState:
        return {
            "name": self.name(),
            "messages": [],
            "chat_model": "",
        }

    @classmethod
    def name(cls) -> str:
        return "Simple Chat"

    @property
    def output_chat_model(self) -> str:
        return "chat_model"

    @classmethod
    def chat_profile(cls) -> cl.ChatProfile:
        return cl.ChatProfile(
            name=cls.name(),
            markdown_description="A ChatGPT-like chatbot.",
            icon="https://cdn1.iconfinder.com/data/icons/3d-front-color/128/chat-text-front-color.png",
            default=True,
            starters=[
                cl.Starter(
                    label="Write a snake game in Python.",
                    message="Write a snake game in Python.",
                    icon="https://cdn1.iconfinder.com/data/icons/photography-calendar-speaker-person-thinking-3d-il/128/13.png",
                ),
                cl.Starter(
                    label="What is the weather in San Francisco?",
                    message="What is the weather in San Francisco?",
                    icon="https://cdn0.iconfinder.com/data/icons/3d-dynamic-color/128/sun-dynamic-color.png",
                ),
                cl.Starter(
                    label="How do I make a peanut butter and jelly sandwich?",
                    message="How do I make a peanut butter and jelly sandwich?",
                    icon="https://cdn0.iconfinder.com/data/icons/fast-food-3d/128/Sandwich.png",
                ),
            ],
        )

    @property
    def default_system_prompt(self) -> str:
        return "You are a helpful assistant."

    @property
    def chat_settings(self) -> cl.ChatSettings:
        return cl.ChatSettings([
            Select(
                id="chat_model",
                label="Chat Model",
                values=sorted(llm_factory.list_models(
                    capabilities=self.capabilities)),
                initial_index=0,
            ),
            TextInput(
                id="chat_system_prompt",
                label="System Prompt",
                initial=self.default_system_prompt,
                multiline=True,
                placeholder="Enter a system prompt for the chatbot.",
            )
        ])
