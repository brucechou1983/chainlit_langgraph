"""
Simple demo of integration with ChainLit and LangGraph.
"""
import chainlit as cl
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import Runnable
from chat_workflow.settings import get_chat_settings
from chat_workflow.module_discovery import discover_modules

discovered_modules = discover_modules()


@cl.on_chat_start
async def on_chat_start():
    print(f"Discovered modules: {discovered_modules}")

    module_name = "base"  # Default module
    create_graph, create_default_state = discovered_modules[module_name]

    print(f"Creating graph for module: {module_name}")

    graph = create_graph()
    state = create_default_state()

    cl.user_session.set("graph", graph.compile())
    cl.user_session.set("state", state)
    cl.user_session.set("current_module", module_name)

    await update_state_by_settings(await get_chat_settings())


@cl.on_message
async def on_message(message: cl.Message):
    # Retrieve the graph and state from the user session
    graph: Runnable = cl.user_session.get("graph")
    state = cl.user_session.get("state")

    # Append the new message to the state
    state["messages"] += [HumanMessage(content=message.content)]

    # Stream the response to the UI
    ui_message = None
    total_content: str = ""
    async for event in graph.astream_events(state, version="v1"):
        # print(f"event: {event}")
        if event["event"] == "on_chat_model_stream" and event["name"] == "chat_model":
            content = event["data"]["chunk"].content or ""
            total_content += content
            if ui_message is None:
                ui_message = cl.Message(content=content)
                await ui_message.send()
            else:
                await ui_message.stream_token(token=content)
    await ui_message.update()

    # Update State
    state["messages"] += [AIMessage(content=total_content)]
    cl.user_session.set("state", state)


@cl.on_settings_update
async def update_state_by_settings(settings: cl.ChatSettings):
    state = cl.user_session.get("state")
    current_module = cl.user_session.get("current_module")

    if "module" in settings and settings["module"] != current_module:
        create_graph, create_default_state = discovered_modules[settings["module"]]
        graph = create_graph()
        state = create_default_state()
        cl.user_session.set("graph", graph.compile())
        cl.user_session.set("current_module", settings["module"])

    for key in settings.keys():
        state[key] = settings[key]

    cl.user_session.set("state", state)
