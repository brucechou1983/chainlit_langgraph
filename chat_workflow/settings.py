import chainlit as cl
from .workflows.base import BaseWorkflow


async def get_chat_settings(workflow: BaseWorkflow) -> cl.ChatSettings:
    return await workflow.chat_settings.send()
