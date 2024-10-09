import os
import chainlit as cl
from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig
from langchain_community.document_loaders import BraveSearchLoader
from langchain_community.tools.tavily_search import TavilySearchResults
from ..graphs import ChatState

load_dotenv()


@cl.step(name="Search", type="tool")
async def search_node(state: ChatState, config: RunnableConfig) -> ChatState:
    # TODO: refactor the available tools list and remove this check
    if state["search_engine"] is None:
        return {
            "tools_to_call": state["tools_to_call"].pop(0),
        }

    # TODO: query rewriting
    query = state["messages"][-1].content

    try:
        pages = None
        result = ""
        if state["search_engine"] == "brave":
            search_engine = BraveSearchLoader(
                api_key=os.getenv("BRAVE_SEARCH_API_KEY"),
                query=query,
                # kwargs reference: https://api.search.brave.com/app/documentation/web-search/query#WebSearchAPI
                # TODO: make it configurable by AI itself
                search_kwargs={"count": 5, "offset": 0},
            )
            pages = [doc.page_content for doc in search_engine.lazy_load()]
            result = "\n".join([f" - {page}" for page in pages])
        elif state["search_engine"] == "tavily":
            search_engine = TavilySearchResults(max_results=5)
            pages = search_engine.invoke(query)
            result = "\n".join([f" - {page['content']}" for page in pages])
        return {
            "tools_to_call": state["tools_to_call"].pop(0),
            "tool_results": state["tool_results"] + [{"name": "search result pages", "value": result}]
        }
    except Exception as e:
        return {
            "tools_to_call": state["tools_to_call"].pop(0),
        }
