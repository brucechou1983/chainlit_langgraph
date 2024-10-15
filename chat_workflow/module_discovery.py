import importlib
import os
from typing import Dict, Type
from .workflows.base import BaseWorkflow


def discover_modules() -> Dict[str, Type[BaseWorkflow]]:
    modules = {}
    workflows_dir = os.path.join(os.path.dirname(__file__), 'workflows')
    for filename in os.listdir(workflows_dir):
        if filename.endswith('.py') and not filename.startswith('__'):
            module_name = filename[:-3]
            module = importlib.import_module(
                f'chat_workflow.workflows.{module_name}')
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, BaseWorkflow) and attr != BaseWorkflow:
                    workflow = attr()
                    modules[workflow.name] = workflow
    return modules
