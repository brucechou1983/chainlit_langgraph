import os
import json
import chainlit as cl
from datetime import datetime
from dotenv import load_dotenv
from langchain_core.messages import AnyMessage, SystemMessage, AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.output_parsers import StrOutputParser, CommaSeparatedListOutputParser
from langgraph.graph import StateGraph, END
from . import ChatState
from ..llm import create_chat_model
# TODO: make it more flexible to add new tools
from ..tools.search import search_node

load_dotenv()

# TODO: refactor
available_tools = [
    {"name": "search", "description": "Search the web. Usually used to answer questions that require real-time information. Or when the user asks for searching directly."},
    {"name": "datetime", "description": "Get the current date and time"},
    # {"name": "python_interpreter", "description": "Write and run Python code"},
]


def create_default_chat_state():
    return {
        "messages": [],
        "chat_model": os.getenv("CHAT_MODEL", "ollama-llama3.2"),
        "tool_results": [],
        "tools_to_call": [],
        "search_engine": None,
    }


async def datetime_node(state: ChatState, config: RunnableConfig) -> ChatState:
    async with cl.Step("Datetime") as step:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        step.output = now
        return {
            "tool_results": state["tool_results"] + [{"name": "datetime", "value": now}],
            "tools_to_call": state["tools_to_call"].pop(0),
        }


async def tool_selection_node(state: ChatState, config: RunnableConfig) -> ChatState:
    system_promopt = """
Your role is to select the most appropriate tools to use based on the user's latest input.

The available tools are:
{available_tools}

Your output should be a comma separated list of tool names like this:

name_of_tool_1,name_of_tool_2

When the user's input needs no tool to answer, just return the word "none".

Note that only use the tools that are listed above, and only use the tools if necessary.

It's important that don't output any other information before or after the list.
"""
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_promopt),
        MessagesPlaceholder(variable_name="recent_history"),
    ])
    prompt = prompt.partial(
        available_tools=json.dumps(available_tools, indent=4))

    llm_settings = {
        "model": state["tool_selection_model"],
    }
    llm = create_chat_model("tool_selection_llm", **llm_settings)
    chain = prompt | llm | CommaSeparatedListOutputParser()
    result = await chain.ainvoke({"recent_history": state["messages"][-5:]})
    result_filtered = [tool for tool in result if tool in [
        tool["name"] for tool in available_tools]]
    return {
        "tools_to_call": result_filtered,
    }


async def chat_node(state: ChatState, config: RunnableConfig) -> ChatState:
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="You're a helpful assistant."),
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


def tool_routing(state: ChatState) -> str:
    print(f"tools_to_call: {state['tools_to_call']}")
    if len(state["tools_to_call"]) == 0:
        return "chat"

    # This is a temporary solution to prevent calling unknown tools
    if state["tools_to_call"][0] in [tool["name"] for tool in available_tools]:
        return state["tools_to_call"][0]

    return "chat"


def create_graph():
    graph = StateGraph(ChatState)
    graph.add_node("tool_selection", tool_selection_node)
    graph.add_node("search", search_node)
    graph.add_node("datetime", datetime_node)
    graph.add_node("chat", chat_node)

    # TODO: create a router for using multiple tools
    graph.add_edge("search", "chat")
    graph.add_edge("datetime", "chat")
    graph.add_edge("chat", END)
    graph.set_entry_point("tool_selection")
    graph.add_conditional_edges("tool_selection", tool_routing)
    return graph
