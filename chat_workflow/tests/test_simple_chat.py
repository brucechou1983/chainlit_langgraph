import pytest
from chainlit.input_widget import Select
from chat_workflow.workflows.simple_chat import SimpleChatWorkflow, GraphState


@pytest.fixture
def simple_chat_workflow():
    return SimpleChatWorkflow()


def test_workflow_initialization(simple_chat_workflow):
    assert isinstance(simple_chat_workflow, SimpleChatWorkflow)
    assert len(simple_chat_workflow.tools) > 0


def test_create_default_state(simple_chat_workflow):
    state = simple_chat_workflow.create_default_state()
    assert isinstance(state, dict)
    assert state["name"] == "Simple Chat"
    assert state["messages"] == []
    assert state["chat_model"] == ""


def test_workflow_name():
    assert SimpleChatWorkflow.name() == "Simple Chat"


def test_chat_profile():
    profile = SimpleChatWorkflow.chat_profile()
    assert profile.name == "Simple Chat"
    assert profile.markdown_description == "A ChatGPT-like chatbot."
    assert profile.default is True
    assert len(profile.starters) == 3


def test_chat_settings(simple_chat_workflow):
    settings = simple_chat_workflow.chat_settings
    assert len(settings.inputs) == 1
    assert isinstance(settings.inputs[0], Select)
    assert settings.inputs[0].id == "chat_model"


def test_create_graph(simple_chat_workflow):
    graph = simple_chat_workflow.create_graph()
    assert graph is not None
    assert "chat" in graph.nodes
    assert "tools" in graph.nodes


@pytest.mark.asyncio
async def test_chat_node():
    workflow = SimpleChatWorkflow()
    state = GraphState(
        name="Simple Chat",
        messages=[],
        chat_model="(openai)gpt-4o-mini"  # Use an appropriate test model
    )
    config = {"configurable": {"session_id": "test_session"}}

    result = await workflow.chat_node(state, config)
    assert isinstance(result, dict)
    assert "messages" in result


def test_graph_state():
    state = GraphState(
        name="Simple Chat",
        messages=[],
        chat_model="(openai)gpt-4o-mini"
    )
    assert state["name"] == "Simple Chat"
    assert len(state["messages"]) == 0
    assert state["chat_model"] == "(openai)gpt-4o-mini"
