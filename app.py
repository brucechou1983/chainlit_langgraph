"""
Simple demo of integration with ChainLit and LangGraph.
"""
import chainlit as cl
import operator
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate, AIMessagePromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_ollama.chat_models import ChatOllama
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Sequence


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


@cl.on_chat_start
async def on_chat_start():
    # start graph
    graph = StateGraph(ChatState)
    graph.add_node("chat", chat_node)
    graph.add_edge("chat", END)
    graph.set_entry_point("chat")

    # initialize state
    state = ChatState(messages=[])

    # save graph and state to the user session
    cl.user_session.set("graph", graph.compile())
    cl.user_session.set("state", state)


@cl.on_message
async def on_message(message: cl.Message):
    # Retrieve the graph and state from the user session
    graph: Runnable = cl.user_session.get("graph")
    state = cl.user_session.get("state")

    # Append the new message to the state
    state["messages"] += [HumanMessage(content=message.content)]

    # Stream the response to the UI
    ui_message = cl.Message(content="")
    await ui_message.send()
    async for event in graph.astream_events(state, version="v1"):
        print(f"event: {event}")
        if event["event"] == "on_chat_model_stream" and event["name"] == "chat_llama3.2":
            content = event["data"]["chunk"].content or ""
            await ui_message.stream_token(token=content)
    await ui_message.update()
