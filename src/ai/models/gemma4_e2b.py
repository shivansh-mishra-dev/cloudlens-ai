from langchain_ollama.chat_models import ChatOllama
import logging


logger = logging.getLogger(__name__)


def gemma4e2b():
    """
    Instantiates the local Ollama LLM connector.
    """

    try:
        llm = ChatOllama(
            model="gemma4:e2b", base_url="http://localhost:11434", temperature=0.0
        )

        return llm
    except Exception as e:
        logger.error(f"Failed to connect local Ollama llm : {str(e)}")
        raise
