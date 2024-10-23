import importlib
import os
from .workflows.base import BaseWorkflow
from .workflows.workflow_factory import WorkflowFactory


def discover_workflows():
    workflows_dir = os.path.join(os.path.dirname(__file__), 'workflows')
    for filename in os.listdir(workflows_dir):
        if filename.endswith('.py') and not filename.startswith('__'):
            module_name = filename[:-3]
            module = importlib.import_module(
                f'chat_workflow.workflows.{module_name}')
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, BaseWorkflow) and attr != BaseWorkflow:
                    # Register discovered workflow with factory
                    WorkflowFactory.register(attr().name, attr)
