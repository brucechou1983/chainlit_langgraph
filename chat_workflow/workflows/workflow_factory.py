import chainlit as cl
import importlib
from typing import Type, Dict
from .base import BaseWorkflow, BaseState


class WorkflowFactory:
    _workflows: Dict[str, Type[BaseWorkflow]] = {}
    _module_map: Dict[str, str] = {}  # Maps chat profile names to module names

    @classmethod
    def register(cls, name: str, workflow_class: Type[BaseWorkflow]):
        module_name = workflow_class.__module__.split(
            '.')[-1]  # e.g. 'simple_chat'
        cls._workflows[name] = workflow_class  # e.g. 'Simple Chat'
        cls._module_map[name] = module_name

    @classmethod
    def unregister(cls, name: str):
        """Dynamically remove workflows"""
        cls._workflows.pop(name, None)

    @classmethod
    def create(cls, name: str, **kwargs) -> BaseWorkflow:
        if name not in cls._workflows:
            raise ValueError(f"Workflow {name} not found")
        return cls._workflows[name](**kwargs)

    @classmethod
    def list_workflows(cls) -> list[str]:
        return list(cls._workflows.keys())

    @classmethod
    def get_graph_state(cls, chat_profile: str) -> Type[BaseState]:
        """Get GraphState using chat profile name"""
        workflow_class = cls._workflows[chat_profile]
        module = importlib.import_module(workflow_class.__module__)
        return getattr(module, "GraphState")

    @classmethod
    def get_chat_profile(cls, name: str) -> cl.ChatProfile:
        """Get chat profile from workflow class"""
        workflow_class = cls._workflows[name]
        return workflow_class.chat_profile()
