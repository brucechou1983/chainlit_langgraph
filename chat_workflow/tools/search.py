# from dotenv import load_dotenv
# from langchain_community.document_loaders import BraveSearchLoader
from langchain_community.tools.tavily_search import TavilySearchResults

# load_dotenv()


async def search(query: str) -> str:
    """
    Search the web to fact checking, getting latest or real-time information.

    Args:
        query: The query to search for
    """
    search_engine = TavilySearchResults(max_results=5)
    pages = await search_engine.ainvoke(query)
    result = "\n".join([f" - {page['content']}" for page in pages])
    return result
