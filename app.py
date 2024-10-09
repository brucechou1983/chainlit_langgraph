"""
Simple demo of integration with ChainLit and LangGraph.
"""
import chainlit as cl
from chat_workflow.graphs.base import create_graph, create_default_chat_state, ChatState
from chat_workflow.settings import get_chat_settings
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import Runnable


@cl.on_chat_start
async def on_chat_start():
    # start graph
    graph = create_graph()

    # initialize state
    state = create_default_chat_state()

    # save graph and state to the user session
    cl.user_session.set("graph", graph.compile())
    cl.user_session.set("state", state)

    # Chat Settings
    await update_state_by_settings(await get_chat_settings())


@cl.on_message
async def on_message(message: cl.Message):
    # Retrieve the graph and state from the user session
    graph: Runnable = cl.user_session.get("graph")
    state: ChatState = cl.user_session.get("state")

    # Append the new message to the state
    state["messages"] += [HumanMessage(content=message.content)]

    # Stream the response to the UI
    ui_message = cl.Message(content="")
    await ui_message.send()
    total_content: str = ""
    async for event in graph.astream_events(state, version="v1"):
        # print(f"event: {event}")
        if event["event"] == "on_chat_model_stream" and event["name"] == "chat_model":
            content = event["data"]["chunk"].content or ""
            total_content += content
            await ui_message.stream_token(token=content)
    await ui_message.update()

    # Update State
    state["messages"] += [AIMessage(content=total_content)]
    cl.user_session.set("state", state)


@cl.on_settings_update
async def update_state_by_settings(settings: cl.ChatSettings):
    state = cl.user_session.get("state")
    for key in settings.keys():
        state[key] = settings[key]
