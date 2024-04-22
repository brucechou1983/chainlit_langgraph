# Chainlit Langgraph integration

## Installation

### Python requirements

In your Python 3.10 virtual env, install all deps by running:

```
pip install --upgrade pip
pip install poetry
poetry install
```

### Ollama

This demo uses `Llama 3` via Ollama by default.

Download and install [Ollama](https://ollama.com/), and run

```bash
ollama pull llama3
ollama serve
```

## Usage

```bash
chainlit run app.py --port 8000
```