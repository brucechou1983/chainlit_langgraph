import os
from dotenv import load_dotenv
from openai import OpenAI
from typing import List

load_dotenv()


def list_xai_models() -> List[str]:
    """
    List all available XAI models

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
        client = OpenAI(api_key=os.getenv("XAI_API_KEY"),
                        base_url=os.getenv("XAI_BASE_URL"))
        response = client.models.list()
        return [f'{model.id}' for model in response.data]
    except Exception as e:
        return []
