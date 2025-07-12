"""
OpenRouter service for LLM access and CrewAI integration.

This module provides functionality for interacting with OpenRouter API,
including LLM client management, error handling, retry logic, and rate limiting.
"""

import logging
import time
import asyncio
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from pathlib import Path

import httpx
from pydantic import BaseModel, Field

from src.models.config_models import Config

logger = logging.getLogger(__name__)


class OpenRouterMessage(BaseModel):
    """Message model for OpenRouter API."""
    
    role: str = Field(..., description="Message role (system, user, assistant)")
    content: str = Field(..., description="Message content")


class OpenRouterRequest(BaseModel):
    """Request model for OpenRouter API."""
    
    model: str = Field(..., description="Model to use for generation")
    messages: List[OpenRouterMessage] = Field(..., description="List of messages")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Temperature for generation")
    max_tokens: int = Field(default=4000, ge=1, le=8192, description="Maximum tokens to generate")
    top_p: float = Field(default=1.0, ge=0.0, le=1.0, description="Top-p sampling parameter")
    frequency_penalty: float = Field(default=0.0, ge=-2.0, le=2.0, description="Frequency penalty")
    presence_penalty: float = Field(default=0.0, ge=-2.0, le=2.0, description="Presence penalty")
    stream: bool = Field(default=False, description="Whether to stream the response")


class OpenRouterResponse(BaseModel):
    """Response model for OpenRouter API."""
    
    id: str = Field(..., description="Response ID")
    model: str = Field(..., description="Model used")
    created: int = Field(..., description="Creation timestamp")
    choices: List[Dict[str, Any]] = Field(..., description="Generated choices")
    usage: Dict[str, int] = Field(..., description="Token usage information")


class RateLimiter:
    """Rate limiter for API requests."""
    
    def __init__(self, max_requests: int, time_window: int):
        """Initialize rate limiter."""
        self.max_requests = max_requests
        self.time_window = time_window  # in seconds
        self.requests = []
    
    async def acquire(self) -> bool:
        """Acquire permission to make a request."""
        now = time.time()
        
        # Remove old requests outside the time window
        self.requests = [req_time for req_time in self.requests if now - req_time < self.time_window]
        
        if len(self.requests) >= self.max_requests:
            return False
        
        self.requests.append(now)
        return True
    
    async def wait_for_slot(self) -> None:
        """Wait until a request slot is available."""
        while not await self.acquire():
            await asyncio.sleep(1)


class OpenRouterService:
    """Service for interacting with OpenRouter API."""
    
    def __init__(self, config: Config):
        """Initialize OpenRouter service."""
        self.config = config
        self.api_key = config.api.openrouter_api_key
        self.base_url = config.api.openrouter_base_url
        
        # Initialize rate limiter
        self.rate_limiter = RateLimiter(
            max_requests=config.security.rate_limit_requests_per_minute,
            time_window=60
        )
        
        # Initialize HTTP client
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(
                connect=config.security.connect_timeout,
                read=config.security.request_timeout,
                write=config.security.request_timeout,
                pool=30.0
            ),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": f"NotesToBlog/{config.app.app_version}"
            }
        )
        
        # Only validate if we have a real API key
        if self.api_key and self.api_key != "your_openrouter_api_key_here":
            self._validate_configuration()
        else:
            logger.warning("OpenRouter API key not configured - service will fail when used")
    
    def _validate_configuration(self) -> None:
        """Validate service configuration."""
        if not self.api_key or self.api_key == "your_openrouter_api_key_here":
            raise ValueError("OpenRouter API key not configured")
        
        if not self.base_url:
            raise ValueError("OpenRouter base URL not configured")
        
        logger.info(f"OpenRouter service initialized with base URL: {self.base_url}")
    
    def _check_api_key(self) -> None:
        """Check if API key is properly configured before making requests."""
        if not self.api_key or self.api_key == "your_openrouter_api_key_here":
            raise ValueError("OpenRouter API key not configured. Please set OPENROUTER_API_KEY in your .env file")
    
    async def generate_text(
        self,
        messages: List[Dict[str, str]],
        model: str = "openai/gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate text using OpenRouter API."""
        
        try:
            # Check API key before making request
            self._check_api_key()
            
            # Wait for rate limit slot
            await self.rate_limiter.wait_for_slot()
            
            # Prepare request
            request_data = OpenRouterRequest(
                model=model,
                messages=[OpenRouterMessage(**msg) for msg in messages],
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            # Make API request with retry logic
            response = await self._make_request_with_retry(request_data)
            
            # Parse response
            parsed_response = OpenRouterResponse(**response)
            
            logger.debug(f"Generated text using model {model}, tokens used: {parsed_response.usage}")
            
            return {
                "success": True,
                "content": parsed_response.choices[0]["message"]["content"],
                "model": parsed_response.model,
                "usage": parsed_response.usage,
                "response_id": parsed_response.id
            }
            
        except Exception as e:
            logger.error(f"Failed to generate text: {e}")
            return {
                "success": False,
                "error": str(e),
                "content": None
            }
    
    async def _make_request_with_retry(self, request_data: OpenRouterRequest) -> Dict[str, Any]:
        """Make API request with retry logic."""
        
        max_retries = self.config.crewai.agent_max_retries
        retry_delay = 1.0
        
        for attempt in range(max_retries + 1):
            try:
                response = await self.client.post(
                    f"{self.base_url}/chat/completions",
                    json=request_data.model_dump()
                )
                
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:  # Rate limit
                    retry_after = int(e.response.headers.get("Retry-After", retry_delay))
                    logger.warning(f"Rate limited, retrying after {retry_after} seconds")
                    await asyncio.sleep(retry_after)
                    retry_delay *= 2
                elif e.response.status_code >= 500:  # Server error
                    logger.warning(f"Server error {e.response.status_code}, attempt {attempt + 1}/{max_retries + 1}")
                    if attempt < max_retries:
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2
                    else:
                        raise
                else:
                    # Client error, don't retry
                    raise
                    
            except httpx.RequestError as e:
                logger.warning(f"Request error: {e}, attempt {attempt + 1}/{max_retries + 1}")
                if attempt < max_retries:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    raise
        
        raise Exception(f"Failed after {max_retries + 1} attempts")
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models."""
        
        try:
            # Check API key before making request
            self._check_api_key()
            
            await self.rate_limiter.wait_for_slot()
            
            response = await self.client.get(f"{self.base_url}/models")
            response.raise_for_status()
            
            data = response.json()
            return data.get("data", [])
            
        except Exception as e:
            logger.error(f"Failed to get available models: {e}")
            return []
    
    async def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific model."""
        
        try:
            # Check API key before making request
            self._check_api_key()
            
            await self.rate_limiter.wait_for_slot()
            
            response = await self.client.get(f"{self.base_url}/models/{model_id}")
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to get model info for {model_id}: {e}")
            return None
    
    def create_crewai_adapter(self):
        """Create adapter for CrewAI integration."""
        
        class OpenRouterCrewAIAdapter:
            """Adapter for CrewAI to use OpenRouter service."""
            
            def __init__(self, service: OpenRouterService):
                self.service = service
            
            def call(self, prompt: str, **kwargs) -> str:
                """Synchronous call method for CrewAI compatibility."""
                
                try:
                    # Create a simple async function to run
                    async def _generate():
                        messages = [{"role": "user", "content": prompt}]
                        result = await self.service.generate_text(
                            messages=messages,
                            **kwargs
                        )
                        if result["success"]:
                            return result["content"]
                        else:
                            raise Exception(f"Generation failed: {result['error']}")
                    
                    # Run in a new event loop to avoid conflicts
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            # Create a new event loop in a separate thread
                            import concurrent.futures
                            with concurrent.futures.ThreadPoolExecutor() as executor:
                                future = executor.submit(asyncio.run, _generate())
                                return future.result()
                        else:
                            return loop.run_until_complete(_generate())
                    except RuntimeError:
                        # No event loop, create one
                        return asyncio.run(_generate())
                        
                except Exception as e:
                    logger.error(f"Error in OpenRouter adapter call: {e}")
                    raise
            
            def generate(self, prompt: str, **kwargs) -> str:
                """Alias for call method."""
                return self.call(prompt, **kwargs)
            
            def sync_generate(self, prompt: str, **kwargs) -> str:
                """Alias for call method."""
                return self.call(prompt, **kwargs)
        
        return OpenRouterCrewAIAdapter(self)
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of the service."""
        
        try:
            # Check if API key is configured
            if not self.api_key or self.api_key == "your_openrouter_api_key_here":
                return {
                    "status": "unhealthy",
                    "error": "OpenRouter API key not configured",
                    "timestamp": datetime.now().isoformat()
                }
            
            start_time = time.time()
            
            # Test with a simple prompt
            messages = [{"role": "user", "content": "Hello, this is a health check."}]
            
            result = await self.generate_text(
                messages=messages,
                model="openai/gpt-3.5-turbo",
                max_tokens=10
            )
            
            response_time = time.time() - start_time
            
            return {
                "status": "healthy" if result["success"] else "unhealthy",
                "response_time": response_time,
                "error": result.get("error"),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def close(self) -> None:
        """Close the service and cleanup resources."""
        
        await self.client.aclose()
        logger.info("OpenRouter service closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        asyncio.create_task(self.close()) 