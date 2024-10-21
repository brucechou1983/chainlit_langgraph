import chainlit as cl
from chainlit import logger
from pypdf import PdfReader
from chainlit.input_widget import Select
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig
from typing import Sequence
from .base import BaseWorkflow, BaseState
from ..llm import create_chat_model, list_available_llm
from ..tools import BasicToolNode
from ..tools.search import search
from ..tools.time import get_datetime_now


class GraphState(BaseState):
    # Model name of the chatbot
    chat_model: str

    # Resume text
    resume_text: str

    # Job descriptions
    # job_descriptions: Sequence[str]


class ResumeOptimizerWorkflow(BaseWorkflow):
    def __init__(self):
        super().__init__()

        # TODO: check tool availability
        # self.tools = [get_datetime_now, search]

    def create_graph(self) -> StateGraph:
        graph = StateGraph(GraphState)
        # Nodes
        graph.add_node("resume_extractor", self.resume_extractor_node)
        graph.add_node("chat", self.chat_node)
        # graph.add_node("tools", BasicToolNode(self.tools))

        # Edges
        graph.add_edge("resume_extractor", "chat")
        graph.add_edge("chat", END)
        # graph.add_conditional_edges("chat", self.tool_routing)

        # Entry point
        graph.set_conditional_entry_point(
            lambda state: "resume_extractor" if state["resume_text"] == "" else "chat",
        )
        return graph

    async def resume_extractor_node(self, state: GraphState, config: RunnableConfig) -> GraphState:
        files = None

        # Wait for the user to upload a file
        while files == None:
            files = await cl.AskFileMessage(
                content="Please upload your resume PDF to begin!", accept=["application/pdf"],
            ).send()

        # Check if the file is a PDF
        resume_text = ""
        if files[0].name.endswith(".pdf"):
            # Read the PDF file
            pdf_reader = PdfReader(files[0].path)

            # Extract the text from the PDF
            for page in pdf_reader.pages:
                resume_text += page.extract_text()

        # TODO: optimize the resume text using LLM

        return {
            "messages": [HumanMessage(content=resume_text)],
            "resume_text": resume_text,
        }

    async def chat_node(self, state: GraphState, config: RunnableConfig) -> GraphState:

        # logger.info(f"State: {state}")
        system_prompt = SystemMessagePromptTemplate.from_template("""
You are a helpful assistant that helps users optimize their resumes for job applications. 

** Guidelines **
1. Is the Resume Summary and Career Objective Clear?
- Is it concise and does it highlight the candidate's professional strengths and goals?
- Is it relevant to the job being applied for?
2. Does the Skills Section Align with the Job Requirements?
- Does the technical stack include skills valued by the employer?
- Does it avoid outdated technologies and focus on core skills from the job description?
3. Is Work Experience Quantified with Results?
_ Are achievements presented with specific data or percentages (e.g., performance improvement or cost reduction)?
_ Does it emphasize the impact of their contributions, such as faster delivery times or higher user satisfaction?
4. Is the Format Clear and Well-Organized?
_  Are sections and paragraphs clearly separated (e.g., using bold headings and bullet points)?
_  Is the content concise and easy to read?
5. Is the Project Experience Detailed and Precise?
_  Does it clearly describe the project’s goal, technology stack, and the candidate's specific contributions?
_  Are the project outcomes presented clearly and effectively?
6. Does the Resume Match the Target Position?
_  Has the resume been adjusted for the specific job (e.g., keywords optimized for the role)?
_  Does it emphasize relevant experience and skills required by the role?
7. Is the Language Professional and Free of Errors?
_  Has the resume been checked for spelling and grammar mistakes?
_  Is the wording professional and free of unnecessary or vague descriptions?
8. Are Certifications and Credentials Relevant?
_  Does it list certifications that add value to the applied role?
_  Does it only include certifications relevant to the candidate's career path?
9. Is Open Source Contribution or Technical Work Demonstrated?
_  Does the resume include links to GitHub projects or other technical portfolios?
_  Does it describe the candidate’s role and contributions to open-source projects?
10. Is Contact Information Complete and Correct?
_  Does it include a valid phone number and email address?
_  Are LinkedIn or other portfolio links included?

Based on the above guidelines, please provide a detailed and specific modification suggestions on the resume.

""")

        prompt = ChatPromptTemplate.from_messages([
            system_prompt,
            MessagesPlaceholder(variable_name="messages"),
        ])

        logger.info(f"Prompt: {prompt}")
        llm = create_chat_model(self.output_chat_model,
                                model=state["chat_model"])
        chain: Runnable = prompt | llm
        return {
            "messages": [await chain.ainvoke({"messages": state["messages"]}, config=config)]
        }

    def create_default_state(self) -> GraphState:
        return {
            "name": self.name,
            "messages": [],
            "chat_model": "",
            "resume_text": "",
        }

    @property
    def name(self) -> str:
        return "Resume Optimizer"

    @property
    def output_chat_model(self) -> str:
        return "chat_model"

    @property
    def chat_profile(self) -> cl.ChatProfile:
        return cl.ChatProfile(
            name=self.name,
            markdown_description="An assistant that helps users optimize their resumes.",
            icon="https://picsum.photos/152",
        )

    @property
    def chat_settings(self) -> cl.ChatSettings:
        return cl.ChatSettings([
            Select(
                id="chat_model",
                label="Chat Model",
                values=sorted(list_available_llm()),
                initial_index=1,
            ),
        ])
