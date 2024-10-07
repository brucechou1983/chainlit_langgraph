"""
Simple demo of integration with ChainLit and LangGraph.
"""
import chainlit as cl
from chat_workflow.graphs.base import ChatState, create_graph
from langchain_core.messages import HumanMessage
from langchain_core.runnables import Runnable


@cl.on_chat_start
async def on_chat_start():
    # start graph
    graph = create_graph()

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
