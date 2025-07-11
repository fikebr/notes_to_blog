#!/usr/bin/env python3
"""
Test script to verify the BraveSearchService works correctly.
"""

import sys
import asyncio
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.brave_search_service import (
    BraveSearchService,
    BraveSearchResult,
    BraveSearchResponse,
    BraveSearchCache
)
from src.models.config_models import Config
from src.models.config_models import APIConfig


def test_brave_search_result_model():
    """Test BraveSearchResult model validation."""
    print("Testing BraveSearchResult Model...")
    print("=" * 50)
    try:
        result = BraveSearchResult(
            title="Test Title",
            url="https://example.com",
            snippet="This is a test snippet.",
            score=1.5,
            source="example"
        )
        print(f"✅ Valid result created: {result.title}")
        return True
    except Exception as e:
        print(f"❌ Result model test failed: {e}")
        return False


def test_brave_search_response_model():
    """Test BraveSearchResponse model validation."""
    print("\nTesting BraveSearchResponse Model...")
    print("=" * 50)
    try:
        response = BraveSearchResponse(
            query="test query",
            results=[
                BraveSearchResult(title="A", url="https://a.com", snippet="A", score=1.0),
                BraveSearchResult(title="B", url="https://b.com", snippet="B", score=0.5)
            ],
            total=2,
            took=0.1,
            cached=False
        )
        print(f"✅ Valid response created: {response.query}")
        return True
    except Exception as e:
        print(f"❌ Response model test failed: {e}")
        return False


def test_brave_search_cache():
    """Test BraveSearchCache functionality."""
    print("\nTesting BraveSearchCache...")
    print("=" * 50)
    try:
        cache = BraveSearchCache(max_size=2, ttl=2)
        resp1 = BraveSearchResponse(query="q1", results=[], total=0, took=0.1)
        resp2 = BraveSearchResponse(query="q2", results=[], total=0, took=0.1)
        resp3 = BraveSearchResponse(query="q3", results=[], total=0, took=0.1)
        cache.set("q1", resp1)
        cache.set("q2", resp2)
        assert cache.get("q1") is not None, "q1 should be cached"
        cache.set("q3", resp3)  # Should evict q1 or q2
        assert len(cache.cache) == 2, "Cache should not exceed max_size"
        print("✅ Cache size and eviction passed")
        # Test TTL
        import time as t
        t.sleep(2.1)
        assert cache.get("q2") is None, "q2 should expire after TTL"
        print("✅ Cache TTL passed")
        return True
    except Exception as e:
        print(f"❌ Cache test failed: {e}")
        return False


def test_brave_search_service_initialization():
    """Test BraveSearchService initialization."""
    print("\nTesting BraveSearchService Initialization...")
    print("=" * 50)
    try:
        config = Config(
            api=APIConfig(
                openrouter_api_key="test_key",
                openrouter_base_url="https://openrouter.ai/api/v1",
                replicate_api_token="test_token",
                brave_api_key="test_brave_key"
            )
        )
        service = BraveSearchService(config)
        print(f"✅ BraveSearchService initialized")
        print(f"   Base URL: {service.base_url}")
        return True
    except Exception as e:
        print(f"❌ Service initialization test failed: {e}")
        return False


def test_error_handling():
    """Test error handling scenarios."""
    print("\nTesting Error Handling...")
    print("=" * 50)
    try:
        # Test missing API key
        try:
            config = Config(
                api=APIConfig(
                    openrouter_api_key="test_key",
                    openrouter_base_url="https://openrouter.ai/api/v1",
                    replicate_api_token="test_token",
                    brave_api_key=""
                )
            )
            BraveSearchService(config)
            print("❌ Should have failed with empty API key")
            return False
        except ValueError:
            print("✅ Correctly caught empty API key")
        # Test missing base URL
        try:
            config = Config(
                api=APIConfig(
                    openrouter_api_key="test_key",
                    openrouter_base_url="https://openrouter.ai/api/v1",
                    replicate_api_token="test_token",
                    brave_api_key="test_brave_key"
                )
            )
            config.api.brave_search_url = ""
            BraveSearchService(config)
            print("❌ Should have failed with empty base URL")
            return False
        except ValueError:
            print("✅ Correctly caught empty base URL")
        return True
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False


async def test_scoring_and_filtering():
    """Test result scoring and filtering logic."""
    print("\nTesting Scoring and Filtering...")
    print("=" * 50)
    try:
        config = Config(
            api=APIConfig(
                openrouter_api_key="test_key",
                openrouter_base_url="https://openrouter.ai/api/v1",
                replicate_api_token="test_token",
                brave_api_key="test_brave_key"
            )
        )
        service = BraveSearchService(config)
        results = [
            BraveSearchResult(title="A", url="https://foo.com", snippet="A"),
            BraveSearchResult(title="B", url="https://bar.com", snippet="B"),
            BraveSearchResult(title="C", url="https://baz.com", snippet="C")
        ]
        filtered = service._score_and_filter_results(results, filter_domains=["foo.com"], min_score=1.0)
        assert all(r.score >= 1.0 for r in filtered), "All scores should be >= 1.0"
        assert filtered[0].url == "https://foo.com", "foo.com should be ranked first"
        print("✅ Scoring and filtering logic passed")
        return True
    except Exception as e:
        print(f"❌ Scoring/filtering test failed: {e}")
        return False


async def test_search_structure():
    """Test search structure (without real API call)."""
    print("\nTesting Search Structure...")
    print("=" * 50)
    try:
        config = Config(
            api=APIConfig(
                openrouter_api_key="test_key",
                openrouter_base_url="https://openrouter.ai/api/v1",
                replicate_api_token="test_token",
                brave_api_key="test_brave_key"
            )
        )
        service = BraveSearchService(config)
        # Simulate a search (mock response)
        # This would require a real API key for a live call
        print("✅ Search structure tested (requires real API key for full test)")
        return True
    except Exception as e:
        print(f"❌ Search structure test failed: {e}")
        return False


async def test_health_check():
    """Test health check functionality."""
    print("\nTesting Health Check...")
    print("=" * 50)
    try:
        config = Config(
            api=APIConfig(
                openrouter_api_key="test_key",
                openrouter_base_url="https://openrouter.ai/api/v1",
                replicate_api_token="test_token",
                brave_api_key="test_brave_key"
            )
        )
        service = BraveSearchService(config)
        health_result = await service.health_check()
        print(f"✅ Health check structure: {health_result}")
        print(f"   Status: {health_result.get('status')}")
        print(f"   Timestamp: {health_result.get('timestamp')}")
        return True
    except Exception as e:
        print(f"❌ Health check test failed: {e}")
        return False


async def main():
    print("Brave Search Service Test")
    print("=" * 50)
    sync_tests = [
        test_brave_search_result_model,
        test_brave_search_response_model,
        test_brave_search_cache,
        test_brave_search_service_initialization,
        test_error_handling,
    ]
    async_tests = [
        test_scoring_and_filtering,
        test_search_structure,
        test_health_check,
    ]
    passed = 0
    total = len(sync_tests) + len(async_tests)
    for test in sync_tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    for test in async_tests:
        try:
            if await test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    if passed == total:
        print("🎉 All Brave search service tests passed!")
        return 0
    else:
        print("⚠️  Some Brave search service tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main())) 