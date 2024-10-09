import chainlit as cl
from chainlit.input_widget import Select

chat_models = ["ollama-llama3.2", "claude-3-5-sonnet-20240620", "gpt-4o"]
tool_selection_models = ["ollama-llama3.2",
                         "claude-3-haiku-20240307", "gpt-4o-mini"]


async def get_chat_settings() -> cl.ChatSettings:

    settings = await cl.ChatSettings(
        [
            Select(
                id="chat_model",
                label="Chat Model",
                values=chat_models,
                initial_index=0,
            ),
            Select(
                id="tool_selection_model",
                label="Tool Selection Model",
                values=tool_selection_models,
                initial_index=0,
            ),
            # Select(
            #     id="graph",
            #     label="Graph for the demo",
            #     values=graph_names,
            #     initial_index=0,
            # ),
        ]
    ).send()
    return settings
