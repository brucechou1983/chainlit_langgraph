from typing import Protocol, runtime_checkable
from enum import Enum, auto


class ModelCapability(Enum):
    TEXT_TO_TEXT = auto()
    TEXT_TO_IMAGE = auto()
    IMAGE_TO_TEXT = auto()
    IMAGE_TO_IMAGE = auto()
    TOOL_CALLING = auto()
    STRUCTURED_OUTPUT = auto()
    AUDIO_TO_TEXT = auto()
    TEXT_TO_AUDIO = auto()
    AUDIO_TO_AUDIO = auto()
    TEXT_EMBEDDING = auto()


@runtime_checkable
class CapableModel(Protocol):
    def get_capabilities(self) -> set[ModelCapability]:
        """Return set of capabilities this model supports"""
        pass
