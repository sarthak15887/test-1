from typing import List, Optional, Dict, Any
from langchain_core.messages import BaseMessage
import litellm
from datetime import datetime

from app.core.config import get_settings
from app.core.logging_config import get_logger

settings = get_settings()
logger = get_logger(__name__)


class LLMService:
    """Unified LLM service with multi-provider support via LiteLLM."""
    
    def __init__(self):
        self.default_model = settings.DEFAULT_LLM_MODEL
        self.default_provider = settings.DEFAULT_LLM_PROVIDER
        
        # Configure LiteLLM if master key is provided
        if settings.LITELM_MASTER_KEY:
            litellm.master_key = settings.LITELM_MASTER_KEY
        
        # Set API keys for providers
        if settings.OPENAI_API_KEY:
            litellm.openai_api_key = settings.OPENAI_API_KEY
        
        if settings.ANTHROPIC_API_KEY:
            litellm.anthropic_api_key = settings.ANTHROPIC_API_KEY
        
        if settings.AZURE_OPENAI_API_KEY and settings.AZURE_OPENAI_ENDPOINT:
            litellm.azure_key = settings.AZURE_OPENAI_API_KEY
            litellm.api_base = settings.AZURE_OPENAI_ENDPOINT
    
    def generate(
        self,
        messages: List[BaseMessage],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> Any:
        """Generate a response from the LLM."""
        model_name = model or self.default_model
        
        # Convert LangChain messages to LiteLLM format
        litellm_messages = self._convert_messages(messages)
        
        try:
            response = litellm.completion(
                model=model_name,
                messages=litellm_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
                **kwargs
            )
            
            if stream:
                return response
            
            # Track usage
            if hasattr(response, 'usage'):
                logger.info(
                    "LLM generation completed",
                    model=model_name,
                    tokens_used=response.usage.total_tokens,
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens
                )
            
            return response.choices[0].message
        
        except Exception as e:
            logger.error("LLM generation failed", error=str(e), model=model_name)
            raise
    
    async def generate_async(
        self,
        messages: List[BaseMessage],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> Any:
        """Generate a response asynchronously."""
        model_name = model or self.default_model
        litellm_messages = self._convert_messages(messages)
        
        try:
            response = await litellm.acompletion(
                model=model_name,
                messages=litellm_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
                **kwargs
            )
            
            if stream:
                return response
            
            if hasattr(response, 'usage'):
                logger.info(
                    "Async LLM generation completed",
                    model=model_name,
                    tokens_used=response.usage.total_tokens
                )
            
            return response.choices[0].message
        
        except Exception as e:
            logger.error("Async LLM generation failed", error=str(e), model=model_name)
            raise
    
    def _convert_messages(self, messages: List[BaseMessage]) -> List[Dict[str, str]]:
        """Convert LangChain messages to LiteLLM format."""
        litellm_messages = []
        
        for msg in messages:
            if hasattr(msg, 'type'):
                role = msg.type
            else:
                role = type(msg).__name__.lower()
            
            # Map roles
            if role == 'human':
                role = 'user'
            elif role == 'ai':
                role = 'assistant'
            elif role == 'system':
                role = 'system'
            
            content = msg.content if hasattr(msg, 'content') else str(msg)
            litellm_messages.append({"role": role, "content": content})
        
        return litellm_messages
    
    def estimate_cost(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int
    ) -> float:
        """Estimate the cost of an LLM call."""
        try:
            cost = litellm.cost_calculator.completion_cost(
                model=model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens
            )
            return cost
        except Exception:
            # Return 0 if cost calculation fails
            return 0.0
    
    def list_available_models(self) -> List[Dict[str, Any]]:
        """List available models from configured providers."""
        # Common models across providers
        models = [
            {"provider": "openai", "model": "gpt-4o", "context_window": 128000},
            {"provider": "openai", "model": "gpt-4-turbo", "context_window": 128000},
            {"provider": "openai", "model": "gpt-3.5-turbo", "context_window": 16385},
            {"provider": "anthropic", "model": "claude-3-5-sonnet", "context_window": 200000},
            {"provider": "anthropic", "model": "claude-3-opus", "context_window": 200000},
            {"provider": "anthropic", "model": "claude-3-haiku", "context_window": 200000},
        ]
        
        # Filter based on configured API keys
        available = []
        if settings.OPENAI_API_KEY:
            available.extend([m for m in models if m["provider"] == "openai"])
        if settings.ANTHROPIC_API_KEY:
            available.extend([m for m in models if m["provider"] == "anthropic"])
        
        return available if available else models


# Singleton instance
_llm_service_instance: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get or create the LLM service singleton."""
    global _llm_service_instance
    if _llm_service_instance is None:
        _llm_service_instance = LLMService()
    return _llm_service_instance
