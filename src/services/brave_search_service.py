"""
Brave Browser API service for web search.

This module provides functionality for interacting with the Brave Search API,
including web search, result filtering, relevance scoring, caching, and error handling.
"""

import logging
import time
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import hashlib

import httpx
from pydantic import BaseModel, Field

from models import Config

logger = logging.getLogger(__name__)


class BraveSearchResult(BaseModel):
    """Model for a single Brave search result."""
    title: str
    url: str
    snippet: str
    score: float = 0.0
    source: Optional[str] = None


class BraveSearchResponse(BaseModel):
    """Model for Brave search API response."""
    query: str
    results: List[BraveSearchResult]
    total: int
    took: float
    cached: bool = False
    error: Optional[str] = None


class BraveSearchCache:
    """Simple in-memory cache for search results."""
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.max_size = max_size
        self.ttl = ttl
        self.cache: Dict[str, Tuple[float, BraveSearchResponse]] = {}

    def _make_key(self, query: str) -> str:
        return hashlib.sha256(query.encode()).hexdigest()

    def get(self, query: str) -> Optional[BraveSearchResponse]:
        key = self._make_key(query)
        entry = self.cache.get(key)
        if entry:
            timestamp, value = entry
            if time.time() - timestamp < self.ttl:
                return value
            else:
                del self.cache[key]
        return None

    def set(self, query: str, value: BraveSearchResponse):
        key = self._make_key(query)
        if len(self.cache) >= self.max_size:
            # Remove oldest
            oldest = min(self.cache.items(), key=lambda x: x[1][0])[0]
            del self.cache[oldest]
        self.cache[key] = (time.time(), value)

    def clear(self):
        self.cache.clear()


class BraveSearchService:
    """Service for interacting with Brave Search API."""
    
    def __init__(self, config: Config):
        self.config = config
        self.api_key = config.api.brave_api_key
        self.base_url = config.api.brave_search_url
        self.cache = BraveSearchCache(
            max_size=config.storage.cache_max_size,
            ttl=config.storage.cache_ttl
        )
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(
                connect=10.0,
                read=30.0,
                write=10.0,
                pool=30.0
            ),
            headers={
                "Accept": "application/json",
                "X-Subscription-Token": self.api_key,
                "User-Agent": f"NotesToBlog/{config.app.app_version}"
            }
        )
        self._validate_configuration()

    def _validate_configuration(self) -> None:
        if not self.api_key or self.api_key == "your_brave_api_key_here":
            raise ValueError("Brave API key not configured")
        if not self.base_url:
            raise ValueError("Brave search URL not configured")
        logger.info(f"Brave search service initialized with base URL: {self.base_url}")

    async def search(
        self,
        query: str,
        num_results: int = 10,
        filter_domains: Optional[List[str]] = None,
        min_score: float = 0.0
    ) -> BraveSearchResponse:
        """Perform a web search using Brave API."""
        # Check cache first
        cached = self.cache.get(query)
        if cached:
            logger.info(f"Cache hit for query: {query}")
            cached.cached = True
            return cached
        try:
            params = {
                "q": query,
                "count": num_results,
                "safesearch": "moderate",
                "result_filter": "web"
            }
            response = await self.client.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            web_results = data.get("web", {}).get("results", [])
            results = []
            for item in web_results:
                result = BraveSearchResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    snippet=item.get("description", ""),
                    source=item.get("source", None)
                )
                results.append(result)
            # Score and filter
            results = self._score_and_filter_results(results, filter_domains, min_score)
            resp = BraveSearchResponse(
                query=query,
                results=results,
                total=len(results),
                took=response.elapsed.total_seconds(),
                cached=False
            )
            self.cache.set(query, resp)
            return resp
        except Exception as e:
            logger.error(f"Brave search failed: {e}")
            return BraveSearchResponse(
                query=query,
                results=[],
                total=0,
                took=0.0,
                cached=False,
                error=str(e)
            )

    def _score_and_filter_results(
        self,
        results: List[BraveSearchResult],
        filter_domains: Optional[List[str]],
        min_score: float
    ) -> List[BraveSearchResult]:
        # Simple scoring: boost if domain matches, penalize otherwise
        for r in results:
            r.score = 1.0
            if filter_domains:
                if any(domain in r.url for domain in filter_domains):
                    r.score += 1.0
                else:
                    r.score -= 0.5
        # Filter by min_score
        filtered = [r for r in results if r.score >= min_score]
        # Sort by score descending
        filtered.sort(key=lambda r: r.score, reverse=True)
        return filtered

    async def health_check(self) -> Dict[str, Any]:
        try:
            start_time = time.time()
            result = await self.search("Brave Search health check", num_results=1)
            response_time = time.time() - start_time
            return {
                "status": "healthy" if result.total > 0 else "unhealthy",
                "response_time": response_time,
                "error": result.error,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def close(self) -> None:
        await self.client.aclose()
        logger.info("Brave search service closed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        asyncio.create_task(self.close()) 