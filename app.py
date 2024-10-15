"""
Simple demo of integration with ChainLit and LangGraph.
"""
import chainlit as cl
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import Runnable
from chat_workflow.settings import get_chat_settings
from chat_workflow.module_discovery import discover_modules

discovered_workflows = discover_modules()


@cl.on_chat_start
async def on_chat_start():
    print(f"Discovered workflows: {discovered_workflows}")
    workflow_name = "simple_chat"  # Default workflow
    workflow = discovered_workflows[workflow_name]

    graph = workflow.create_graph()
    state = workflow.create_default_state()

    cl.user_session.set("graph", graph.compile())
    cl.user_session.set("state", state)
    cl.user_session.set("current_workflow", workflow_name)

    await update_state_by_settings(await get_chat_settings(discovered_workflows.keys()))


@cl.on_settings_update
async def update_state_by_settings(settings: cl.ChatSettings):
    state = cl.user_session.get("state")
    current_workflow = cl.user_session.get("current_workflow")

    # Update the workflow if the workflow setting has changed
    if "workflow" in settings and settings["workflow"] != current_workflow:
        workflow = discovered_workflows[settings["workflow"]]
        graph = workflow.create_graph()
        state = workflow.create_default_state()
        cl.user_session.set("graph", graph.compile())
        cl.user_session.set("current_workflow", settings["workflow"])

    # TODO: Update UI based on the selected workflow

    for key in settings.keys():
        state[key] = settings[key]

    cl.user_session.set("state", state)


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
        string_content = ""
        if event["event"] == "on_chat_model_stream" and event["name"] == "chat_model":
            content = event["data"]["chunk"].content or ""
            if type(content) == str:
                string_content += content
            elif type(content) == list and len(content) > 0:
                if type(content[0]) == str:
                    string_content += " ".join(content)
                elif type(content[0]) == dict and "text" in content[0]:
                    string_content += " ".join([c["text"] for c in content])
            else:
                string_content = ""
            total_content += string_content
            if ui_message is None:
                ui_message = cl.Message(content=string_content)
                await ui_message.send()
            else:
                await ui_message.stream_token(token=string_content)
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
