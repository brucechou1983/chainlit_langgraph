import os
from dotenv import load_dotenv
# from langchain_community.document_loaders import BraveSearchLoader
from typing import List, Callable
from langchain_community.tools.tavily_search import TavilySearchResults

load_dotenv()


def is_search_tool_available() -> bool:
    """
    Check if the search tool is available.
    """
    # Check Tavily API key is set
    return os.getenv("TAVILY_API_KEY") is not None


async def tavily_search(query: str) -> str:
    """
    Search the web to fact checking, getting latest or real-time information.

    Args:
        query: The query to search for
    """
    search_engine = TavilySearchResults(max_results=5)
    pages = await search_engine.ainvoke(query)
    result = "\n".join([f" - {page['content']}" for page in pages])
    return result


# A function that return a list of async search functions if the search tool is available
def get_search_tools() -> List[Callable]:
    if is_search_tool_available():
        return [tavily_search]
    else:
        return []
