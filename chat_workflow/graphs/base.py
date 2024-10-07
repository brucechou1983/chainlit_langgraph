import operator
import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import AnyMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END
from ..llm import create_chat_model


class ChatState(TypedDict):
    # Message history
    messages: Annotated[Sequence[AnyMessage], operator.add]

    # Model name of the chatbot
    chat_model: str


def create_default_chat_state():
    return {
        "messages": [],
        "chat_model": os.getenv("CHAT_MODEL", "ollama-llama3.2"),
    }


async def chat_node(state: ChatState, config: RunnableConfig) -> ChatState:
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(
            content="You're a careful thinker. Think step by step before answering."),
        MessagesPlaceholder(variable_name="messages"),
    ])
    llm = create_chat_model("chat_model", model=state["chat_model"])
    chain: Runnable = prompt | llm | StrOutputParser()
    response = await chain.ainvoke(state, config=config)
    return {
        "messages": [AIMessage(content=response)]
    }


def create_graph():
    graph = StateGraph(ChatState)
    graph.add_node("chat", chat_node)
    graph.add_edge("chat", END)
    graph.set_entry_point("chat")
    return graph
