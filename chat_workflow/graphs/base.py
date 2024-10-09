import os
from dotenv import load_dotenv
from langchain_core.messages import AnyMessage, SystemMessage, AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END
from . import ChatState
from ..llm import create_chat_model
# TODO: make it more flexible to add new tools
from ..tools.search.brave import search_node

load_dotenv()


def create_default_chat_state():
    return {
        "messages": [],
        "chat_model": os.getenv("CHAT_MODEL", "ollama-llama3.2"),
        "tool_results": [],
    }


async def chat_node(state: ChatState, config: RunnableConfig) -> ChatState:
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(
            content="You're a careful thinker. Think step by step before answering."),
        MessagesPlaceholder(variable_name="history"),
    ])
    llm = create_chat_model("chat_model", model=state["chat_model"])
    chain: Runnable = prompt | llm | StrOutputParser()

    # Append search results to the message history
    if len(state["tool_results"]) > 0:
        last_msg = state["messages"][-1].content + "\n" + \
            "\n".join(
                f"{result['name']}: \n{result['value']}" for result in state["tool_results"])
        history = state["messages"][:-1] + [HumanMessage(content=last_msg)]
    else:
        history = state["messages"]
    response = await chain.ainvoke({"history": history}, config=config)
    return {
        "tool_results": [],
        "messages": [AIMessage(content=response)]
    }


def create_graph():
    graph = StateGraph(ChatState)
    graph.add_node("search", search_node)
    graph.add_node("chat", chat_node)
    graph.add_edge("search", "chat")
    graph.add_edge("chat", END)
    graph.set_entry_point("search")
    return graph
