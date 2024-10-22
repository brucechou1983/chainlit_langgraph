import json
from typing import Type
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from chat_workflow.workflows.base import BaseState


class StateSerializer:
    """
    A utility class for serializing and deserializing BaseState objects.

    This class provides methods to convert BaseState objects to and from JSON strings,
    making them suitable for storage in databases or transmission over networks.
    It handles special cases for message objects and provides a generic approach
    for other state attributes.

    Class Methods:
        serialize(state: BaseState) -> str:
            Converts a BaseState object to a JSON string.

        deserialize(serialized_state: str, state_class: Type[BaseState]) -> BaseState:
            Converts a JSON string back to a BaseState object of the specified class.
    """

    @classmethod
    def serialize(cls, state: BaseState) -> str:
        serializable_state = state.copy()
        serializable_state["messages"] = cls._serialize_messages(
            state["messages"])
        return json.dumps(serializable_state, default=cls._json_serializer)

    @classmethod
    def deserialize(cls, serialized_state: str, state_class: Type[BaseState]) -> BaseState:
        state_dict = json.loads(serialized_state)
        state_dict['messages'] = cls._deserialize_messages(
            state_dict['messages'])
        return state_class(**cls._json_deserializer(state_dict))

    @staticmethod
    def _serialize_messages(messages):
        return [message.model_dump() for message in messages]

    @staticmethod
    def _deserialize_messages(serialized_messages):
        """
        Deserialize a list of message dictionaries into their respective BaseMessage subclasses.

        This method takes a list of serialized message dictionaries and converts them back
        into instances of the appropriate BaseMessage subclasses (HumanMessage, AIMessage,
        ToolMessage, SystemMessage) based on the 'type' field in each dictionary.

        Args:
            serialized_messages (List[Dict]): A list of dictionaries representing serialized messages.
                Each dictionary should contain a 'type' field and other relevant message data.

        Returns:
            List[BaseMessage]: A list of deserialized BaseMessage subclass instances.

        Example:
            serialized_messages = [
                {"type": "human", "content": "Hello"},
                {"type": "ai", "content": "Hi there!"},
                {"type": "tool", "content": "Processing...", "tool_call_id": "123"}
            ]
            deserialized_messages = StateSerializer._deserialize_messages(serialized_messages)
        """
        message_type_mapping = {
            "human": HumanMessage,
            "ai": AIMessage,
            "tool": ToolMessage,
            "system": SystemMessage,
        }

        deserialized_messages = []
        for msg_dict in serialized_messages:
            msg_type = msg_dict.get("type")
            msg_class = message_type_mapping.get(msg_type, BaseMessage)
            deserialized_messages.append(msg_class.model_validate(msg_dict))
        return deserialized_messages

    @staticmethod
    def _json_serializer(obj):
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        return str(obj)

    @staticmethod
    def _json_deserializer(dct):
        for key, value in dct.items():
            if isinstance(value, str):
                try:
                    dct[key] = eval(value)
                except:
                    pass
        return dct
