"""
Service Registry for external service adapters.

Provides centralized access, configuration, and health checks for all services.
"""

import logging
from typing import Dict, Any, Optional, Type

from models import Config
from services.openrouter_service import OpenRouterService
from services.replicate_service import ReplicateService
from services.brave_search_service import BraveSearchService

logger = logging.getLogger(__name__)

class ServiceRegistry:
    """Central registry for all external services."""
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self._services: Dict[str, Any] = {}

    def get_openrouter(self) -> OpenRouterService:
        if "openrouter" not in self._services:
            self._services["openrouter"] = OpenRouterService(self.config)
        return self._services["openrouter"]

    def get_replicate(self) -> ReplicateService:
        if "replicate" not in self._services:
            self._services["replicate"] = ReplicateService(self.config)
        return self._services["replicate"]

    def get_brave(self) -> BraveSearchService:
        if "brave" not in self._services:
            self._services["brave"] = BraveSearchService(self.config)
        return self._services["brave"]

    def get_service(self, name: str) -> Any:
        if name == "openrouter":
            return self.get_openrouter()
        elif name == "replicate":
            return self.get_replicate()
        elif name == "brave":
            return self.get_brave()
        else:
            raise ValueError(f"Unknown service: {name}")

    async def health_check_all(self) -> Dict[str, Any]:
        """Run health checks for all services."""
        results = {}
        for name, getter in [
            ("openrouter", self.get_openrouter),
            ("replicate", self.get_replicate),
            ("brave", self.get_brave),
        ]:
            try:
                service = getter()
                if hasattr(service, "health_check"):
                    result = await service.health_check()
                else:
                    result = {"status": "unknown", "error": "No health_check method"}
                results[name] = result
            except Exception as e:
                logger.error(f"Health check failed for {name}: {e}")
                results[name] = {"status": "unhealthy", "error": str(e)}
        return results

    async def close_all(self):
        """Close all services."""
        for service in self._services.values():
            if hasattr(service, "close"):
                await service.close() 