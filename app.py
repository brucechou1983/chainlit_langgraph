"""
Simple demo of integration with ChainLit and LangGraph.
"""
import chainlit as cl
import logging
import os
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import Runnable
from chainlit.logger import logger
from chat_workflow.module_discovery import discover_modules
from dotenv import load_dotenv

load_dotenv()

# Get logging level from environment variable, default to INFO if not set
logging_level = os.getenv('LOGGING_LEVEL', 'INFO').upper()
numeric_level = getattr(logging, logging_level, None)
logger.setLevel(numeric_level)
logger.info(f"Logging level set to: {logging_level} {numeric_level}")

discovered_workflows = discover_modules()
logger.debug(f"Discovered workflows: {list(discovered_workflows.keys())}")


@cl.set_chat_profiles
async def chat_profile():
    profiles = []
    for workflow in discovered_workflows.values():
        profiles.append(workflow.chat_profile)
    logger.debug(f"Chat profiles created: {len(profiles)}")
    return profiles


@cl.on_chat_start
async def on_chat_start():
    workflow_name = cl.context.session.chat_profile
    logger.info(f"Starting chat with workflow: {workflow_name}")
    workflow = discovered_workflows[workflow_name]

    graph = workflow.create_graph()
    state = workflow.create_default_state()

    cl.user_session.set("graph", graph.compile())
    cl.user_session.set("state", state)
    cl.user_session.set("current_workflow", workflow_name)
    logger.debug(f"Initial state set: {state}")

    chat_settings = await workflow.get_chat_settings()
    await update_state_by_settings(chat_settings)
    logger.info("Chat started and initialized")


@cl.on_settings_update
async def update_state_by_settings(settings: cl.ChatSettings):
    state = cl.user_session.get("state")
    logger.info("Updating state based on new settings")
    for key in settings.keys():
        if key not in state:
            logger.warning(f"Setting {key} not found in state")
            continue
        logger.debug(f"Setting {key} to {settings[key]}")
        state[key] = settings[key]
    cl.user_session.set("state", state)
    logger.info("State updated with new settings")


@cl.on_message
async def on_message(message: cl.Message):
    # Log first 50 chars of message
    logger.info(f"Received message: {message.content[:50]}...")

    graph: Runnable = cl.user_session.get("graph")
    state = cl.user_session.get("state")
    current_workflow = cl.user_session.get("current_workflow")
    workflow = discovered_workflows[current_workflow]
    logger.debug(f"Current workflow: {current_workflow}")

    state["messages"] += [HumanMessage(content=message.content)]
    logger.debug(
        f"Updated state with new message. Total messages: {len(state['messages'])}")

    ui_message = None
    total_content: str = ""
    logger.info("Starting to stream response")
    async for event in graph.astream_events(state, version="v1"):
        string_content = ""
        if event["event"] == "on_chat_model_stream" and event["name"] == workflow.output_chat_model:
            content = event["data"]["chunk"].content or ""
            if isinstance(content, str):
                string_content += content
            elif isinstance(content, list) and len(content) > 0:
                if isinstance(content[0], str):
                    string_content += " ".join(content)
                elif isinstance(content[0], dict) and "text" in content[0]:
                    string_content += " ".join([c["text"] for c in content])
            else:
                string_content = ""
            total_content += string_content
            if ui_message is None:
                ui_message = cl.Message(content=string_content)
                await ui_message.send()
                logger.debug("Started new UI message")
            else:
                await ui_message.stream_token(token=string_content)
    await ui_message.update()
    logger.info(
        f"Finished streaming response. Total length: {len(total_content)}")

    state["messages"] += [AIMessage(content=total_content)]
    cl.user_session.set("state", state)
    logger.debug(
        f"Updated state with AI response. Total messages: {len(state['messages'])}")
