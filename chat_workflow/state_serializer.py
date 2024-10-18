import json
from typing import Type
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
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

    Static Methods:
        _serialize_messages(messages: List) -> List[Dict]:
            Converts message objects to serializable dictionaries.

        _deserialize_messages(serialized_messages: List[Dict]) -> List:
            Converts serialized message dictionaries back to message objects.

        _json_serializer(obj: Any) -> Any:
            Custom JSON serializer for handling complex objects.

        _json_deserializer(dct: Dict) -> Dict:
            Custom JSON deserializer for handling serialized complex objects.

    This class can be inherited and extended to handle custom state types
    or to add specific serialization/deserialization logic for new attributes.

    Example:
        class CustomStateSerializer(StateSerializer):
            @classmethod
            def serialize(cls, state: CustomState) -> str:
                # Add custom serialization logic here
                serializable_state = state.copy()

                # Example: Convert a custom attribute to a string
                if 'custom_attribute' in serializable_state:
                    serializable_state['custom_attribute'] = str(serializable_state['custom_attribute'])

                # Call the parent class's serialize method
                return super().serialize(serializable_state)

            @classmethod
            def deserialize(cls, serialized_state: str) -> CustomState:
                # Call the parent class's deserialize method
                state_dict = json.loads(serialized_state)

                # Add custom deserialization logic here
                # Example: Convert the custom attribute back to its original type
                if 'custom_attribute' in state_dict:
                    state_dict['custom_attribute'] = CustomType(state_dict['custom_attribute'])

                return CustomState(**cls._json_deserializer(state_dict))
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
        serialized_messages = []
        for msg in messages:
            if isinstance(msg, (HumanMessage, AIMessage, ToolMessage, SystemMessage)):
                serialized_messages.append({
                    "role": msg.__class__.__name__.lower().replace("message", ""),
                    "content": msg.content
                })
            else:
                raise ValueError(f"Unsupported message type: {type(msg)}")
        return serialized_messages

    @staticmethod
    def _deserialize_messages(serialized_messages):
        message_types = {
            "human": HumanMessage,
            "ai": AIMessage,
            "tool": ToolMessage,
            "system": SystemMessage
        }
        return [message_types[msg['role']](content=msg['content']) for msg in serialized_messages]

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
