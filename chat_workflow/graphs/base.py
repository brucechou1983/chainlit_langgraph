import operator
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import AnyMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_ollama.chat_models import ChatOllama
from langgraph.graph import StateGraph, END
from ..llm import create_chat_model


class ChatState(TypedDict):
    messages: Annotated[Sequence[AnyMessage], operator.add]


async def chat_node(state: ChatState, config: RunnableConfig) -> ChatState:
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(
            content="You're a careful thinker. Think step by step before answering."),
        MessagesPlaceholder(variable_name="messages"),
    ])
    llm = create_chat_model("chat_llama3.2", model="ollama-llama3.2")
    chain: Runnable = prompt | llm
    response = await chain.ainvoke(state, config=config)
    return {
        "messages": [response]
    }


def create_graph():
    graph = StateGraph(ChatState)
    graph.add_node("chat", chat_node)
    graph.add_edge("chat", END)
    graph.set_entry_point("chat")
    return graph
