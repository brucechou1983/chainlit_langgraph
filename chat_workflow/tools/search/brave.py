import os
from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig
from langchain_community.document_loaders import BraveSearchLoader
from ...graphs import ChatState

load_dotenv()


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
        result = "\nsearch results:\n" + \
            "\n".join([f" - {page}" for page in pages])
        print(f"search_node: {result}")
        return {"tool_results": state["tool_results"] + [result]}
    except Exception as e:
        return {}
