import operator
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import AnyMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_ollama.chat_models import ChatOllama
from langgraph.graph import StateGraph, END


class ChatState(TypedDict):
    messages: Annotated[Sequence[AnyMessage], operator.add]


async def chat_node(state: ChatState, config: RunnableConfig) -> ChatState:
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(
            content="You're a careful thinker. Think step by step before answering."),
        MessagesPlaceholder(variable_name="messages"),
    ])
    llm = ChatOllama(name="chat_llama3.2", model="llama3.2", stop=[
        "<|start_header_id|>",
        "<|end_header_id|>",
        "<|eot_id|>",
        "<|reserved_special_token"
    ])
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
