"""
Simple demo of integration with ChainLit and LangGraph.
"""
import chainlit as cl
import chainlit.data as cl_data
import logging
import os
import importlib
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import Runnable
from chainlit.data.sql_alchemy import SQLAlchemyDataLayer
from chainlit.logger import logger
from chainlit.types import ThreadDict
from chat_workflow.module_discovery import discover_modules
from chat_workflow.storage_client import MinIOStorageClient, LangGraph
from chat_workflow.state_serializer import StateSerializer
from dotenv import load_dotenv
from typing import Dict, Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


load_dotenv()

# Get logging level from environment variable, default to INFO if not set
logging_level = os.getenv('LOGGING_LEVEL', 'INFO').upper()
numeric_level = getattr(logging, logging_level, None)
logger.setLevel(numeric_level)
logger.info(f"Logging level set to: {logging_level} {numeric_level}")

discovered_workflows = discover_modules()
logger.debug(f"Discovered workflows: {list(discovered_workflows.keys())}")

pg_url = f"postgresql+asyncpg://{os.getenv('POSTGRES_USER', 'postgres')}:{os.getenv('POSTGRES_PASSWORD', 'postgres')}@{os.getenv('POSTGRES_HOST', 'localhost')}:{os.getenv('POSTGRES_PORT', '5432')}/{os.getenv('POSTGRES_DB', 'postgres')}"

# Persistance Layer
storage_client = MinIOStorageClient(
    bucket=os.getenv("MINIO_BUCKET", "chainlit_langgraph"),
    endpoint_url=os.getenv("MINIO_ENDPOINT_URL", "http://localhost:9000"),
    access_key=os.getenv("MINIO_ACCESS_KEY", "chainlit_langgraph"),
    secret_key=os.getenv("MINIO_SECRET_KEY", "chainlit_langgraph"),
)
cl_data._data_layer = SQLAlchemyDataLayer(
    conninfo=pg_url,
    storage_provider=storage_client
)


@cl.on_chat_end
async def on_chat_end():
    """
    Save the chat state to the database before the chat ends
    """
    state = cl.user_session.get("state")
    workflow_name = state["chat_profile"]
    thread_id = cl.context.session.thread_id

    engine = create_async_engine(pg_url)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async with async_session() as session:
            graph = LangGraph(
                thread_id=thread_id,
                state=StateSerializer.serialize(state),
                workflow=workflow_name,
            )
            session.add(graph)
            await session.commit()
        logger.info(f"Successfully saved LangGraph for thread_id: {thread_id}")
    except Exception as e:
        logger.error(f"Error saving LangGraph: {str(e)}")

# FIXME


@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict):
    # Retrieve the LangGraph from the database
    engine = create_async_engine(pg_url)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False)

    db_graph: Optional[LangGraph] = None
    state: Optional[Dict] = None
    async with async_session() as session:
        db_graph = await session.get(LangGraph, thread["id"])
        if db_graph:
            chat_profile = db_graph.workflow
            workflow = discovered_workflows[chat_profile]
            workflow_module = workflow.__class__.__module__
            GraphState = getattr(importlib.import_module(
                workflow_module), "GraphState")
            state = StateSerializer.deserialize(db_graph.state, GraphState)
            cl.user_session.set("state", state)

    # Load the Graph
    if db_graph:
        await start_langgraph(state["chat_profile"], state)


async def start_langgraph(chat_profile: str, state: Optional[Dict] = None):
    """
    Load the Graph

    Args:
        chat_profile (str): The name of the chat profile to load.
        state (Optional[Dict]): The state to load.
    """
    workflow = discovered_workflows[chat_profile]
    graph = workflow.create_graph()
    cl.user_session.set("graph", graph.compile())
    if state:
        # Resume from previous state
        state["chat_profile"] = chat_profile
        cl.user_session.set("state", state)
        await workflow.get_chat_settings(state)
    else:
        # Create new state
        state = workflow.create_default_state()
        state["chat_profile"] = chat_profile
        cl.user_session.set("state", state)
        await update_state_by_settings(await workflow.get_chat_settings())


@cl.oauth_callback
def oauth_callback(
    provider_id: str,
    token: str,
    raw_user_data: Dict[str, str],
    default_user: cl.User,
) -> Optional[cl.User]:
    # TODO: user filtering
    return default_user


@cl.set_chat_profiles
async def chat_profile():
    profiles = []
    for workflow in discovered_workflows.values():
        profiles.append(workflow.chat_profile)
    logger.debug(f"Chat profiles created: {len(profiles)}")
    return profiles


@cl.on_chat_start
async def on_chat_start():
    await start_langgraph(cl.context.session.chat_profile)
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
    workflow = discovered_workflows[state["chat_profile"]]
    logger.debug(f"Chat Profile: {chat_profile}")

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
