import chainlit as cl
import json
from typing import List, Dict, Optional
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableConfig, Runnable


class BasicToolNode(Runnable):
    """A node that runs the tools requested in the last AIMessage."""

    def __init__(self, tools: List) -> None:
        self.tools_by_name = {tool.__name__: tool for tool in tools}

    async def ainvoke(self, inputs: Dict, config: Optional[RunnableConfig] = None) -> Dict:
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No message found in input")
        outputs = []
        for tool_call in message.tool_calls:
            async with cl.Step(f"tool [{tool_call['name']}]") as step:
                tool_result = await self.tools_by_name[tool_call["name"]](**tool_call["args"])
                outputs.append(
                    ToolMessage(
                        content=json.dumps(tool_result),
                        name=tool_call["name"],
                        tool_call_id=tool_call["id"],
                    )
                )
                await step.remove()
        return {"messages": outputs}

    def invoke(self, input: Dict, config: Optional[RunnableConfig] = None) -> Dict:
        raise NotImplementedError(
            "BasicToolNode only supports async invocation")
