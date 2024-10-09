import operator
import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import AnyMessage, SystemMessage, AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END
from langchain_community.document_loaders import BraveSearchLoader
from ..llm import create_chat_model

load_dotenv()


# TODO: a middleware to patch the state definition based on the tool used
class ChatState(TypedDict):
    # Message history
    messages: Annotated[Sequence[AnyMessage], operator.add]

    # Model name of the chatbot
    chat_model: str

    # Tool messages which will be appended to the messages
    tool_results: Sequence[str]


def create_default_chat_state():
    return {
        "messages": [],
        "chat_model": os.getenv("CHAT_MODEL", "ollama-llama3.2"),
        "tool_results": [],
    }


async def search_node(state: ChatState, config: RunnableConfig) -> ChatState:
    search_engine = BraveSearchLoader(
        api_key=os.getenv("BRAVE_SEARCH_API_KEY"),

        # TODO: query rewriting
        query=state["messages"][-1].content,

        # kwargs reference: https://api.search.brave.com/app/documentation/web-search/query#WebSearchAPI
        # TODO: make it configurable by AI itself
        search_kwargs={"count": 5, "offset": 0},
    )
    try:
        pages = [doc.page_content for doc in search_engine.lazy_load()]
        result = "\nsearch results:\n" + \
            "\n".join([f" - {page}" for page in pages])
        print(f"search_node: {result}")
        return {"tool_results": state["tool_results"] + [result]}
    except Exception as e:
        return {}


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
            "\n".join(result for result in state["tool_results"])
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
