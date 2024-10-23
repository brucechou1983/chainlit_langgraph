from typing import Type, Dict
from .base import BaseWorkflow


class WorkflowFactory:
    _workflows: Dict[str, Type[BaseWorkflow]] = {}

    @classmethod
    def register(cls, name: str, workflow_class: Type[BaseWorkflow]):
        cls._workflows[name] = workflow_class

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
