import os
import chainlit as cl
from chainlit.input_widget import Select
from dotenv import load_dotenv
from typing import List

load_dotenv()

chat_models = ["ollama-llama3.2"]

if os.getenv("ANTHROPIC_API_KEY"):
    chat_models.append("claude-3-5-sonnet-20240620")
if os.getenv("OPENAI_API_KEY"):
    chat_models.append("gpt-4o-2024-08-06")


tool_selection_models = ["ollama-llama3.2"]
if os.getenv("ANTHROPIC_API_KEY"):
    tool_selection_models.append("claude-3-5-sonnet-20240620")
if os.getenv("OPENAI_API_KEY"):
    tool_selection_models.append("gpt-4o-mini-2024-07-18")

available_search_engines = []
if os.getenv("TAVILY_API_KEY"):
    available_search_engines.append("tavily")
# if os.getenv("BRAVE_SEARCH_API_KEY"):
#     available_search_engines.append("brave")


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
            values=chat_models,
            initial_index=1,
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
