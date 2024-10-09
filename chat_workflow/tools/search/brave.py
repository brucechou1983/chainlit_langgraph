import os
import chainlit as cl
from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig
from langchain_community.document_loaders import BraveSearchLoader
from ...graphs import ChatState

load_dotenv()


@cl.step(name="Search", type="tool")
async def search_node(state: ChatState, config: RunnableConfig) -> ChatState:
    search_engine = BraveSearchLoader(
        api_key=os.getenv("BRAVE_SEARCH_API_KEY"),

        # TODO: query rewriting
        query=state["messages"][-1].content,

        # kwargs reference: https://api.search.brave.com/app/documentation/web-search/query#WebSearchAPI
        # TODO: make it configurable by AI itself
        search_kwargs={"count": 5, "offset": 0},
    )
    try:
        pages = [doc.page_content for doc in search_engine.lazy_load()]
        result = "\n".join([f" - {page}" for page in pages])
        return {"tool_results": state["tool_results"] + [{"name": "search result pages", "value": result}]}
    except Exception as e:
        return {}
