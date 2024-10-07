# **Chainlit Langgraph Integration**  
An integration of Chainlit with Langgraph, leveraging state-of-the-art LLMs including **Llama 3.2** via **Ollama**, **Claude 3.5 Sonnet**, and **GPT-4o** for advanced language processing and interaction.

![Demo](./public/screenshot.png)

## **Overview**
This repository provides a demo showcasing the integration between Chainlit and Langgraph, designed to facilitate seamless communication between systems using state-of-the-art language models. Whether you're working with conversational AI or need a robust language model for text-based tasks, this project helps streamline the process with support for multiple LLMs.

## **Features**
- **Chainlit**: A powerful tool for creating interactive interfaces for AI models.
- **Langgraph**: Enables structured data integration and interaction.
- **Multiple LLM Support**: 
  - **Llama 3.2** via **Ollama**: High-performance open-source language model.
  - **Claude 3.5 Sonnet**: Advanced AI model by Anthropic.
  - **GPT-4**: State-of-the-art language model by OpenAI.
- Easy-to-follow setup with **Poetry** for dependency management.

## Upcoming Features
- **Multi-Step Examples**: Explore a variety of use cases with multi-step examples.
- **Image Input**: User can upload images and interact with them.
- **Image Generation**: Generate images based on user input.
- **OpenAI o1-like agents**: Advanced self-prompting agents.
  
## **Installation Guide**
Follow these steps to set up and run the project in your Python 3.10 virtual environment.

### **Step 1: Python Requirements**
Make sure you have Python 3.10 installed. Then, install the necessary dependencies by running the following commands:

```bash
pip install --upgrade pip
pip install poetry
poetry install
```

### **Step 2: Setting Up LLMs**
This demo supports multiple LLMs. Setup the appropriate environment variables.

#### Ollama (for Llama 3.2):
1. Download and install [Ollama](https://ollama.com/download).
2. Pull the required Llama model:

```bash
ollama pull llama3.2
```

3. Start the Ollama server:

```bash
ollama serve
```


#### Claude 3.5 Sonnet:
1. Sign up for an Anthropic API key at [anthropic](https://www.anthropic.com/api)
2. Set your API key as an environment variable:

export ANTHROPIC_API_KEY=your_api_key_here

#### GPT-4o:
1. Sign up for an OpenAI API key at [OpenAI](https://openai.com/index/openai-api/)
2. Set your API key as an environment variable:

export OPENAI_API_KEY=your_api_key_here


Please note that you can select the LLM for the chatbot in the settings menu next to the text field in the demo.

### **Step 3: Running the Demo**
After completing the above steps, run the Chainlit demo using the following command:

```bash
chainlit run app.py --port 8000
```


This will start the demo on **port 8000**, providing a user interface to interact with the Langgraph integration powered by your chosen LLM.

## **Usage Examples**
- **Conversational AI**: Utilize Chainlit to create conversational interfaces that can be integrated into websites or apps.
- **Text Processing**: Leverage advanced natural language understanding for tasks like summarization, translation, or Q&A.

## **Additional Resources**
- [Chainlit Documentation](https://docs.chainlit.io/get-started/overview)
- [Langgraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Ollama Llama 3.2 Model Info](https://ollama.com/library/llama3.2)
