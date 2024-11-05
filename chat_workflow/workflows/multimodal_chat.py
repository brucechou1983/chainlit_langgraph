import chainlit as cl
import base64
from chainlit.input_widget import Select
from langgraph.graph import StateGraph
from langchain_core.messages import SystemMessage, HumanMessage
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


class MultimodalChatWorkflow(BaseWorkflow):
    def __init__(self):
        super().__init__()

        self.capabilities = {
            ModelCapability.TEXT_TO_TEXT, ModelCapability.IMAGE_TO_TEXT, ModelCapability.TOOL_CALLING}
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
            SystemMessage(content="You're a helpful assistant."),
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
        return "Multimodal Chat"

    @property
    def output_chat_model(self) -> str:
        return "chat_model"

    @classmethod
    def chat_profile(cls) -> cl.ChatProfile:
        return cl.ChatProfile(
            name=cls.name(),
            markdown_description="A ChatGPT-like chatbot.",
            icon="https://cdn0.iconfinder.com/data/icons/essential-pack-1-3d/64/picture.png",
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
    def chat_settings(self) -> cl.ChatSettings:
        return cl.ChatSettings([
            Select(
                id="chat_model",
                label="Chat Model",
                values=sorted(llm_factory.list_models(
                    capabilities=self.capabilities)),
                initial_index=0,
            ),
        ])

    def format_message(self, msg: cl.Message) -> HumanMessage:
        """Format chainlit message to LangChain message with multimodal support"""
        if not msg.elements:
            return HumanMessage(content=msg.content)

        # Initialize the multimodal content list
        formatted_content = [{"type": "text", "text": msg.content}]

        # Process images
        images = [file for file in msg.elements if "image" in file.mime]
        for image in images:
            with open(image.path, "rb") as img_file:
                image_data = base64.b64encode(img_file.read()).decode("utf-8")
                formatted_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_data}"
                    }
                })

        return HumanMessage(content=formatted_content)
