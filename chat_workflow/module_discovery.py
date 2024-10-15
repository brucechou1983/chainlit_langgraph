import importlib
import os
from typing import Dict, Tuple, Callable


def discover_modules() -> Dict[str, Tuple[Callable, Callable]]:
    modules = {}
    graphs_dir = os.path.join(os.path.dirname(__file__), 'graphs')
    for filename in os.listdir(graphs_dir):
        if filename.endswith('.py') and not filename.startswith('__'):
            module_name = filename[:-3]
            module = importlib.import_module(
                f'chat_workflow.graphs.{module_name}')
            print(f"module: {module}")
            create_graph = getattr(module, 'create_graph', None)
            create_default_state = getattr(
                module, f'create_default_state', None)
            if create_graph and create_default_state:
                modules[module_name] = (create_graph, create_default_state)
    print(f"Discovered modules: {modules}")
    return modules
