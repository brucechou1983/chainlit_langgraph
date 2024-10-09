import operator
from typing import TypedDict, Annotated, Sequence, Dict
from langchain_core.messages import AnyMessage


# TODO: a middleware to patch the state definition based on the tool used
class ChatState(TypedDict):
    # Message history
    messages: Annotated[Sequence[AnyMessage], operator.add]

    # Model name of the chatbot
    chat_model: str

    # Model name of the tool selection model
    tool_selection_model: str

    # Tool messages which will be appended to the messages
    tool_results: Sequence[Dict[str, str]]

    # Tool names to call
    tools_to_call: Sequence[str]
