import json
from typing import List, Dict
from langchain_core.messages import ToolMessage


class BasicToolNode:
    """A node that runs the tools requested in the last AIMessage."""

    def __init__(self, tools: List) -> None:
        self.tools_by_name = {tool.__name__: tool for tool in tools}

    def __call__(self, inputs: Dict):
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No message found in input")
        outputs = []
        for tool_call in message.tool_calls:
            print(f"tool_call: {tool_call}")
            tool_result = self.tools_by_name[tool_call["name"]](
                **tool_call["args"]
            )
            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
        return {"messages": outputs}
