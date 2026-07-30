"""
BuildWise AI — Base Agent Class
"""
from abc import ABC, abstractmethod
from typing import Any
import structlog

logger = structlog.get_logger()


class BaseAgent(ABC):
    """Base class for all BuildWise AI agents."""

    name: str = "base_agent"
    description: str = "Base agent"

    def __init__(self):
        self._setup_llm()

    def _setup_llm(self):
        """Initialize the LLM client."""
        from config import settings
        try:
            if settings.USE_OLLAMA:
                from langchain_community.llms import Ollama
                self.llm = Ollama(base_url=settings.OLLAMA_BASE_URL, model=settings.OLLAMA_MODEL)
            else:
                from langchain_openai import ChatOpenAI
                self.llm = ChatOpenAI(
                    model=settings.LLM_MODEL,
                    api_key=settings.OPENAI_API_KEY,
                    base_url=settings.OPENAI_BASE_URL,
                    temperature=0.1,
                )
        except Exception as e:
            logger.warning(f"LLM setup failed, using mock: {e}")
            self.llm = None

    async def run(self, state: dict) -> dict:
        """Execute the agent and return updated state."""
        logger.info(f"Agent running: {self.name}")
        try:
            return await self._execute(state)
        except Exception as e:
            logger.error(f"Agent {self.name} error: {e}")
            state.setdefault("errors", []).append(f"{self.name}: {str(e)}")
            return await self._fallback(state)

    @abstractmethod
    async def _execute(self, state: dict) -> dict:
        pass

    async def _fallback(self, state: dict) -> dict:
        """Return state unchanged on error."""
        return state

    async def _call_llm(self, prompt: str) -> str:
        """Call the LLM and return text response."""
        if self.llm is None:
            return self._mock_response(prompt)
        try:
            from langchain_core.messages import HumanMessage
            if hasattr(self.llm, "invoke"):
                response = self.llm.invoke([HumanMessage(content=prompt)])
                return response.content if hasattr(response, "content") else str(response)
            else:
                return self.llm(prompt)
        except Exception as e:
            logger.warning(f"LLM call failed: {e}, using mock")
            return self._mock_response(prompt)

    def _mock_response(self, prompt: str) -> str:
        """Mock response when LLM is unavailable."""
        return f"[Mock response from {self.name}]"
