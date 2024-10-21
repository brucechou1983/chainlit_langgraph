# **Chainlit LangGraph Chatbot**

[![Chainlit](https://img.shields.io/badge/Chainlit-1.3.0rc1-brightgreen)](https://github.com/Chainlit/chainlit)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2.39-brightgreen)](https://github.com/langchain-ai/langgraph)[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
Rapidly build and deploy production-ready conversational AI agents using Chainlit and LangGraph. This powerful integration combines state-of-the-art language models with flexible workflow management, enabling developers to create sophisticated chatbots, virtual assistants, and interactive AI applications in minutes.

![Demo](./resource/screenshot.gif)

## Table of Contents
- [**Chainlit LangGraph Chatbot**](#chainlit-langgraph-chatbot)
  - [Table of Contents](#table-of-contents)
  - [**Why This Project?**](#why-this-project)
  - [**Features**](#features)
  - [**Getting Started**](#getting-started)
    - [Setting up Ollama (Optional)](#setting-up-ollama-optional)
  - [**Workflows**](#workflows)
    - [Simple Chat Workflow](#simple-chat-workflow)
    - [Resume Optimizer](#resume-optimizer)
    - [Lean Canvas Chat](#lean-canvas-chat)
    - [**Creating Your Own Workflow**](#creating-your-own-workflow)
  - [Upcoming Features](#upcoming-features)

## **Why This Project?**
[Chainlit](https://github.com/Chainlit/chainlit) is a powerful tool for building production-ready conversational AI applications. [LangGraph](https://github.com/langchain-ai/langgraph), on the other hand, is a versatile framework for building and managing state graphs in AI applications. This project combines these two to provide a comprehensive solution for building conversational AI agents, in minutes.

## **Features**
- **Building Blocks**: Utilize a variety of building blocks to create your own conversational AI agents.
- **Multiple LLM Support**: Automatically detects and uses the following LLMs:
  - **Ollama**: Open source model.
  - **Claude**: Advanced AI models by Anthropic.
  - **GPT**: Advanced AI models by OpenAI.
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


## **Workflows**
This project includes several pre-built workflows to demonstrate the capabilities of the Chainlit Langgraph integration:

### [Simple Chat Workflow](./chat_workflow/workflows/simple_chat.py)
Located in `simple_chat.py`, this workflow provides a basic chatbot experience:
- Utilizes a state graph with chat and tool nodes
- Supports multiple language models
- Includes basic tools like datetime and web search

### [Resume Optimizer](./chat_workflow/workflows/resume_optimizer.py)
Found in `resume_optimizer.py`, this workflow helps users improve their resumes:
- Features a resume extractor node to process uploaded PDF resumes
- Provides detailed analysis and suggestions for resume improvement

### [Lean Canvas Chat](./chat_workflow/workflows/lean_canvas_chat.py)
Implemented in `lean_canvas_chat.py`, this workflow assists in business modeling:
- Guides users through the Lean Canvas creation process
- Offers a structured approach to defining business models

Each workflow demonstrates different aspects of the Chainlit Langgraph integration, showcasing its flexibility and power in creating AI-driven applications.

### **Creating Your Own Workflow**
- Inherit from the `BaseWorkflow` and `BaseState` classes. For more details, refer to the [Simple Chat Workflow](./chat_workflow/workflows/simple_chat.py) example.
- Place your workflow in the `chat_workflow/workflows` module.

## Upcoming Features
- **Graph Builder**: A meta-workflow builder that allows users to create custom workflows with natural language.
- **OpenAI o1-like agentic workflow**: Advanced self-prompting agentic workflow.
- **Image Input**: User can upload images and interact with them.
- **Image Generation**: Generate images based on user input.
