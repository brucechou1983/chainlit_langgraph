import chainlit as cl
from chainlit.input_widget import Select
from typing import List
from .llm import list_available_llm
from .workflows.base import BaseWorkflow


async def get_chat_settings(workflow: BaseWorkflow) -> cl.ChatSettings:
    return await workflow.chat_settings.send()
