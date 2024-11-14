![](./public/logo_light.png) 
[![Version](https://img.shields.io/badge/Version-0.3.0-blue)](https://github.com/yourusername/chainlit-langgraph)
[![Chainlit](https://img.shields.io/badge/Chainlit-1.3.1-brightgreen)](https://github.com/Chainlit/chainlit)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2.45-brightgreen)](https://github.com/langchain-ai/langgraph)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://buymeacoffee.com/brucechou1x)

Rapidly build and deploy production-ready conversational AI agents using Chainlit and LangGraph. This powerful integration combines state-of-the-art language models with flexible workflow management, enabling developers to create sophisticated chatbots, virtual assistants, and interactive AI applications in minutes.

![Demo](./resource/screenshot.gif)

## Table of Contents
- [Table of Contents](#table-of-contents)
- [**Why This Project?**](#why-this-project)
- [**Features**](#features)
- [**Getting Started**](#getting-started)
  - [Setting up Ollama (Optional)](#setting-up-ollama-optional)
- [**Creating Custom Workflow**](#creating-custom-workflow)
- [**Workflows**](#workflows)
  - [Simple Chat Workflow](#simple-chat-workflow)
  - [Multimodal Chat Workflow](#multimodal-chat-workflow)
  - [Resume Optimizer](#resume-optimizer)
  - [Lean Canvas Chat](#lean-canvas-chat)
- [Upcoming Features](#upcoming-features)

## **Why This Project?**
[Chainlit](https://github.com/Chainlit/chainlit) is a powerful tool for building production-ready conversational AI applications. [LangGraph](https://github.com/langchain-ai/langgraph), on the other hand, is a versatile framework for building and managing state graphs in AI applications. This project combines these two to provide a comprehensive solution for building conversational AI agents, in minutes.

## **Features**
- **Building Blocks**: Utilize a variety of building blocks to create your own conversational AI agents.
- **Multiple LLM Support**: Automatically detects and uses the following LLMs:
  - **Ollama**: Open source model.
  - **Claude**: Advanced AI models by Anthropic. [Apply API Key Here](https://console.anthropic.com/account/keys)
  - **GPT**: Advanced AI models by OpenAI. [Apply API Key Here](https://platform.openai.com/settings/organization/api-keys)
  - **Grok**: Grok models by xAI. [Apply API Key Here](https://docs.x.ai/docs/quickstart#creating-an-api-key)
  - **Groq**: Fast inference service by Groq. [Apply API Key Here](https://console.groq.com/keys)
  - **Gemini**: Google AI models. [Apply API Key Here](https://aistudio.google.com/app/apikey)
- **Examples**: Explore a variety of use cases with conversational AI agents examples.

## **Getting Started**
Follow these steps to set up and run the project using Docker Compose or in your Python 3.10 virtual environment.

1. Make sure you have Docker and Docker Compose installed on your system.
2. Clone this repository and navigate to the project directory.
3. Copy the `.env.example` file to `.env` and update the necessary environment variables:

```bash
cp .env.example .env
```

4. Edit the `.env` file and set the required variables, including:
  - **API keys** (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`): Optional if you use **Ollama**.
  - **DB volume settings** (`POSTGRES_VOLUME_PATH`, `MINIO_VOLUME_PATH`): create mount folders on your host machine and set the paths accordingly.
  - (Optional) `TAVILY_API_KEY` for enabling search
  - (Optional) Google OAuth
  - (Optional) LangSmith

5. Start the services using Docker Compose

```bash
docker compose up
```

This will start all the necessary services, including the Chainlit application, PostgreSQL database, and MinIO object storage.

6. The application should now be running at http://localhost:8000. Log in with the default username and password (admin:admin). You can change the default credentials in the `.env` file.

### Setting up Ollama (Optional)

1. Download and install [Ollama](https://ollama.com).
2. Pull whatever model you want to use, for example: 

```bash
ollama pull cas/ministral-8b-instruct-2410_q4km:latest
ollama pull llama3.2:3b-instruct-q8_0
```

of any gguf-based model on the [HuggingFace](https://huggingface.co/docs/hub/ollama).

```bash
ollama run hf.co/{username}/{repository}:{quantization}
```

![](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/ollama/guide.png)

## **Creating Custom Workflow**
Creating your own custom workflow allows you to tailor the application to your specific needs. Follow the step-by-step guide below to create your own workflow.

1. Go to the `chat_workflow/workflows` directory in your project, and create a new Python file for your workflow, e.g., `my_custom_workflow.py`.
2. Define Your State Class
  - Inherit from `BaseState` to define the state variables your workflow will use. For example:
  ```python
  class MyCustomState(BaseState):
    # Model name of the chatbot
    chat_model: str
    # Add other state variables as needed
  ```
3. Define Your Workflow
  - Inherit from `BaseWorkflow` to define your custom workflow logic, and override the `create_graph` method to define the state graph.
  ```python
  class MyCustomWorkflow(BaseWorkflow):
    def create_graph(self) -> StateGraph:
        # LangGraph graph definition
        graph = StateGraph(MyCustomState)
        # Add nodes to the graph
        graph.add_node("chat", self.chat_node)
        # Add edges between nodes
        graph.add_edge("chat", END)
        # Set the entry point of the graph
        graph.set_entry_point("chat")
        return graph
  ```
  - Define node methods like `self.chat_node` in the `create_graph` method.
  - Define default state by overriding the `get_default_state` method.
  ```python
  def create_default_state(self) -> MyCustomState:
    return {
        "name": self.name(),
        "messages": [],
        "chat_model": "",
        # Initialize other state variables if needed
    }
  ```
  - Set workflow properties.
    - name: The display name of the workflow. For example, "My Custom Workflow".
    - output_chat_model: The name of the LLM model to provide final output as a response.
    - chat_profile: The profile for the workflow.
    - starter: The starter message for the workflow.

## **Workflows**
This project includes several pre-built workflows to demonstrate the capabilities of the Chainlit Langgraph integration:

### [Simple Chat Workflow](./chat_workflow/workflows/simple_chat.py)
Located in `simple_chat.py`, this workflow provides a basic chatbot experience:
- Utilizes a state graph with chat and tool nodes
- Supports multiple language models
- Includes basic tools like datetime and web search

### [Multimodal Chat Workflow](./chat_workflow/workflows/multimodal_chat.py)
- Supports images and text inputs

### [Resume Optimizer](./chat_workflow/workflows/resume_optimizer.py)
Found in `resume_optimizer.py`, this workflow helps users improve their resumes:
- Features a resume extractor node to process uploaded PDF resumes
- Provides detailed analysis and suggestions for resume improvement

### [Lean Canvas Chat](./chat_workflow/workflows/lean_canvas_chat.py)
Implemented in `lean_canvas_chat.py`, this workflow assists in business modeling:
- Guides users through the Lean Canvas creation process
- Offers a structured approach to defining business models

Each workflow demonstrates different aspects of the Chainlit Langgraph integration, showcasing its flexibility and power in creating AI-driven applications.


## Upcoming Features
- **Research Assistant**: A research assistant that can help users with their general research tasks, like NotebookLM.
- **NVIDIA NIM**: Self-host GPU-accelerated inferencing microservices for pretrained and customized AI models across clouds, data centers, and workstations.
- **Cloud Deployment**: Easy deployment of the application to cloud platforms like AWS, Azure, or GCP.
- **Graph Builder**: A meta-workflow builder that allows users to create custom workflows with natural language.
- **OpenAI o1-like agentic workflow**: Advanced self-prompting agentic workflow.
- **Image Generation**: Generate images based on user input.
