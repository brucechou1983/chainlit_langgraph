import os
from dotenv import load_dotenv
from typing import List

load_dotenv()


def list_anthropic_models() -> List[str]:
    """
    List all available Anthropic models

    Currently, the Anthropic Python module does not offer a direct API 
    endpoint to list all available Claude models.
    """
    if os.getenv("ANTHROPIC_API_KEY"):
        return ["claude-3-5-haiku-20241022", "claude-3-5-sonnet-20241022"]
    else:
        return []
