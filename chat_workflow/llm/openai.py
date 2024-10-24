from dotenv import load_dotenv
from openai import OpenAI
from typing import List

load_dotenv()


def list_openai_models() -> List[str]:
    """
    List all available OpenAI models

    Sample Response:
    {
      "object": "list",
      "data": [
        {
          "id": "model-id-0",
          "object": "model",
          "created": 1686935002,
          "owned_by": "organization-owner"
        },
        {
          "id": "model-id-1",
          "object": "model",
          "created": 1686935002,
          "owned_by": "organization-owner",
        },
        {
          "id": "model-id-2",
          "object": "model",
          "created": 1686935002,
          "owned_by": "openai"
        },
      ],
      "object": "list"
    }
    """
    try:
        client = OpenAI()
        response = client.models.list()
        # Only use model id starting with "gpt-4o-"
        return [f'{model.id}' for model in response.data if model.id.startswith("gpt-4o-")]
    except Exception as e:
        return []
