import os
import requests
import logging
from typing import List, Optional, Dict, Set
from langchain_groq import ChatGroq
from langchain_core.language_models.chat_models import BaseChatModel
from .base import LLMProvider
from ..capabilities import ModelCapability

logger = logging.getLogger(__name__)


class GroqProvider(LLMProvider):
    def create_model(self, name: str, model: str, tools: Optional[List] = None, **kwargs) -> BaseChatModel:
        llm = ChatGroq(name=name, model=model, **kwargs)
        return llm.bind_tools(tools) if tools else llm

    def list_models(self) -> List[str]:
        """
        List all available Groq models

        Returns:
            List of model IDs, or empty list if API call fails
        """
        try:
            api_key = os.environ.get("GROQ_API_KEY")
            if not api_key:
                logger.warning("GROQ_API_KEY not found in environment variables")
                return []

            url = "https://api.groq.com/openai/v1/models"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            response = requests.get(url, headers=headers, timeout=10)

            # Check HTTP status
            if response.status_code != 200:
                logger.error(f"Groq API request failed with status {response.status_code}: {response.text}")
                return []

            models_data = response.json()

            # Validate response structure
            if not isinstance(models_data, dict) or "data" not in models_data:
                logger.error(f"Unexpected Groq API response structure: {models_data}")
                return []

            return [model["id"] for model in models_data["data"]]

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error when fetching Groq models: {e}")
            return []
        except (KeyError, TypeError, ValueError) as e:
            logger.error(f"Error parsing Groq API response: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error when listing Groq models: {e}")
            return []

    @property
    def name(self) -> str:
        return "groq"

    @property
    def capabilities(self) -> Dict[str, Set[ModelCapability]]:
        return {
            "llama-3.2-3b-preview": {ModelCapability.TEXT_TO_TEXT, ModelCapability.TOOL_CALLING},
            "llama-3.2-11b-vision-preview": {ModelCapability.TEXT_TO_TEXT, ModelCapability.IMAGE_TO_TEXT, ModelCapability.TOOL_CALLING},
            "llama-3.2-90b-vision-preview": {ModelCapability.TEXT_TO_TEXT, ModelCapability.IMAGE_TO_TEXT, ModelCapability.TOOL_CALLING},
            "whisper-large-v3": {ModelCapability.AUDIO_TO_TEXT},
        }
