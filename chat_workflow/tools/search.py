# from dotenv import load_dotenv
# from langchain_community.document_loaders import BraveSearchLoader
from langchain_community.tools.tavily_search import TavilySearchResults

# load_dotenv()


def search(query: str) -> str:
    """
    Search the web for the given query

    Args:
        query: The query to search for
    """
    search_engine = TavilySearchResults(max_results=5)
    pages = search_engine.invoke(query)
    result = "\n".join([f" - {page['content']}" for page in pages])
    return result
