import chainlit as cl
from chainlit.input_widget import Select
from typing import List
from .llm import list_available_llm


async def get_chat_settings(workflows: List) -> cl.ChatSettings:

    setting_items = [
        Select(
            id="workflow",
            label="Workflow",
            values=workflows,
            initial_index=0,
        ),
        Select(
            id="chat_model",
            label="Chat Model",
            values=sorted(list_available_llm()),
            initial_index=0,
        ),
    ]
    # if len(available_search_engines) > 0:
    #     setting_items.append(
    #         Select(
    #             id="search_engine",
    #             label="Search Engine",
    #             values=available_search_engines,
    #             initial_index=0,
    #         )
    #     )

    settings = await cl.ChatSettings(setting_items).send()
    return settings
