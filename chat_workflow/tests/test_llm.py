from chat_workflow.llm.providers.ollama import OllamaProvider

provider = OllamaProvider()


def testparse_ollama_params_empty():
    assert provider.parse_ollama_params("") == {}
    assert provider.parse_ollama_params(None) == {}
    assert provider.parse_ollama_params("    ") == {}


def testparse_ollama_params_numeric():
    # Integer parameters
    input_str = """num_ctx                        4096
num_gpu                        2
num_thread                     4
num_predict                    128
repeat_last_n                  64
top_k                          40"""

    expected = {
        "num_ctx": 4096,
        "num_gpu": 2,
        "num_thread": 4,
        "num_predict": 128,
        "repeat_last_n": 64,
        "top_k": 40
    }
    assert provider.parse_ollama_params(input_str) == expected


def testparse_ollama_params_float():
    # Float parameters
    input_str = """mirostat_eta                   0.1
mirostat_tau                   5.0
repeat_penalty                 1.1
temperature                    0.8
tfs_z                         1.0
top_p                         0.9"""

    expected = {
        "mirostat_eta": 0.1,
        "mirostat_tau": 5.0,
        "repeat_penalty": 1.1,
        "temperature": 0.8,
        "tfs_z": 1.0,
        "top_p": 0.9
    }
    assert provider.parse_ollama_params(input_str) == expected


def testparse_ollama_params_stop():
    # Multiple stop sequences with different formats
    input_str = """stop                           "[INST]"
stop                           '[/INST]'
stop                           </s>
stop                           "User:"
stop                           'Assistant:'"""

    expected = {
        "stop": ["[INST]", "[/INST]", "</s>", "User:", "Assistant:"]
    }
    assert provider.parse_ollama_params(input_str) == expected


def testparse_ollama_params_mixed():
    # Combination of different parameter types
    input_str = """num_ctx                        4096
temperature                    0.8
stop                           "[INST]"
stop                           "[/INST]"
num_gpu                        1
mirostat_eta                   0.1
format                         json
seed                          42"""

    expected = {
        "num_ctx": 4096,
        "temperature": 0.8,
        "stop": ["[INST]", "[/INST]"],
        "num_gpu": 1,
        "mirostat_eta": 0.1,
        "format": "json",
        "seed": 42
    }
    assert provider.parse_ollama_params(input_str) == expected


def testparse_ollama_params_whitespace():
    # Test various whitespace formats
    input_str = """num_ctx              4096
temperature        0.8
stop              "[INST]"
"""

    expected = {
        "num_ctx": 4096,
        "temperature": 0.8,
        "stop": ["[INST]"]
    }
    assert provider.parse_ollama_params(input_str) == expected
