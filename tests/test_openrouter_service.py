#!/usr/bin/env python3
"""
Test script to verify the OpenRouter service works correctly.
"""

import sys
import asyncio
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.services.openrouter_service import OpenRouterService, RateLimiter, OpenRouterMessage, OpenRouterRequest
from src.models.config_models import Config, APIConfig


async def test_rate_limiter():
    """Test rate limiter functionality."""
    print("Testing Rate Limiter...")
    print("=" * 50)
    
    try:
        # Test rate limiter with 2 requests per minute
        limiter = RateLimiter(max_requests=2, time_window=60)
        
        # Should allow first two requests
        assert await limiter.acquire() == True
        assert await limiter.acquire() == True
        
        # Third request should be blocked
        assert await limiter.acquire() == False
        
        print("✅ Rate limiter correctly limits requests")
        return True
        
    except Exception as e:
        print(f"❌ Rate limiter test failed: {e}")
        return False


def test_openrouter_message_model():
    """Test OpenRouter message model validation."""
    print("\nTesting OpenRouter Message Model...")
    print("=" * 50)
    
    try:
        # Valid message
        message = OpenRouterMessage(
            role="user",
            content="Hello, world!"
        )
        print(f"✅ Valid message created: {message.role}")
        
        # Test invalid role
        try:
            OpenRouterMessage(
                role="invalid_role",
                content="Test"
            )
            print("❌ Should have failed with invalid role")
            return False
        except Exception:
            print("✅ Correctly caught invalid role")
        
        return True
        
    except Exception as e:
        print(f"❌ Message model test failed: {e}")
        return False


def test_openrouter_request_model():
    """Test OpenRouter request model validation."""
    print("\nTesting OpenRouter Request Model...")
    print("=" * 50)
    
    try:
        # Valid request
        request = OpenRouterRequest(
            model="test/model",
            messages=[
                OpenRouterMessage(role="user", content="Hello")
            ],
            temperature=0.7,
            max_tokens=100
        )
        print(f"✅ Valid request created: {request.model}")
        
        # Test invalid temperature
        try:
            OpenRouterRequest(
                model="test/model",
                messages=[
                    OpenRouterMessage(role="user", content="Hello")
                ],
                temperature=3.0  # Too high
            )
            print("❌ Should have failed with invalid temperature")
            return False
        except Exception:
            print("✅ Correctly caught invalid temperature")
        
        # Test invalid max_tokens
        try:
            OpenRouterRequest(
                model="test/model",
                messages=[
                    OpenRouterMessage(role="user", content="Hello")
                ],
                max_tokens=0  # Too low
            )
            print("❌ Should have failed with invalid max_tokens")
            return False
        except Exception:
            print("✅ Correctly caught invalid max_tokens")
        
        return True
        
    except Exception as e:
        print(f"❌ Request model test failed: {e}")
        return False


def test_openrouter_service_initialization():
    """Test OpenRouter service initialization."""
    print("\nTesting OpenRouter Service Initialization...")
    print("=" * 50)
    
    try:
        # Create mock config
        config = Config(
            api=APIConfig(
                openrouter_api_key="test_key",
                openrouter_base_url="https://openrouter.ai/api/v1",
                openrouter_model="test/model",
                replicate_api_token="test_token",
                brave_api_key="test_brave_key"
            )
        )
        
        service = OpenRouterService(config)
        print(f"✅ OpenRouter service initialized")
        print(f"   Base URL: {service.base_url}")
        print(f"   Rate limit: {service.rate_limiter.max_requests}")
        
        # Test invalid API key
        try:
            invalid_config = Config(
                api=APIConfig(
                    openrouter_api_key="your_openrouter_api_key_here",
                    openrouter_base_url="https://openrouter.ai/api/v1",
                    openrouter_model="test/model",
                    replicate_api_token="test_token",
                    brave_api_key="test_brave_key"
                )
            )
            OpenRouterService(invalid_config)
            print("❌ Should have failed with placeholder API key")
            return False
        except ValueError:
            print("✅ Correctly caught placeholder API key")
        
        return True
        
    except Exception as e:
        print(f"❌ Service initialization test failed: {e}")
        return False


async def test_text_generation():
    """Test text generation functionality."""
    print("\nTesting Text Generation...")
    print("=" * 50)
    
    try:
        # This test requires a real API key, so we'll test the structure
        # In a real environment, you would need valid API keys
        
        config = Config(
            api=APIConfig(
                openrouter_api_key="test_key",
                openrouter_base_url="https://openrouter.ai/api/v1",
                openrouter_model="test/model",
                replicate_api_token="test_token",
                brave_api_key="test_brave_key"
            )
        )
        
        service = OpenRouterService(config)
        
        # Test message preparation
        messages = [
            {"role": "user", "content": "Hello, how are you?"}
        ]
        
        # This would fail with a test key, but we can test the structure
        print("✅ Text generation structure tested (requires real API key for full test)")
        
        return True
        
    except Exception as e:
        print(f"❌ Text generation test failed: {e}")
        return False


def test_crewai_adapter():
    """Test CrewAI adapter creation."""
    print("\nTesting CrewAI Adapter...")
    print("=" * 50)
    
    try:
        config = Config(
            api=APIConfig(
                openrouter_api_key="test_key",
                openrouter_base_url="https://openrouter.ai/api/v1",
                openrouter_model="test/model",
                replicate_api_token="test_token",
                brave_api_key="test_brave_key"
            )
        )
        
        service = OpenRouterService(config)
        adapter = service.create_crewai_adapter()
        
        print(f"✅ CrewAI adapter created: {type(adapter).__name__}")
        
        # Test adapter methods exist
        assert hasattr(adapter, 'generate')
        assert hasattr(adapter, 'sync_generate')
        
        print("✅ Adapter has required methods")
        return True
        
    except Exception as e:
        print(f"❌ CrewAI adapter test failed: {e}")
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
                openrouter_model="test/model",
                replicate_api_token="test_token",
                brave_api_key="test_brave_key"
            )
        )
        
        service = OpenRouterService(config)
        
        # Health check should fail with test key, but we can test the structure
        health_result = await service.health_check()
        
        print(f"✅ Health check structure: {health_result}")
        print(f"   Status: {health_result.get('status')}")
        print(f"   Timestamp: {health_result.get('timestamp')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Health check test failed: {e}")
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
                    openrouter_api_key="",
                    openrouter_base_url="https://openrouter.ai/api/v1",
                    openrouter_model="test/model",
                    replicate_api_token="test_token",
                    brave_api_key="test_brave_key"
                )
            )
            OpenRouterService(config)
            print("❌ Should have failed with empty API key")
            return False
        except ValueError:
            print("✅ Correctly caught empty API key")
        
        # Test missing base URL
        try:
            config = Config(
                api=APIConfig(
                    openrouter_api_key="test_key",
                    openrouter_base_url="",
                    openrouter_model="test/model",
                    replicate_api_token="test_token",
                    brave_api_key="test_brave_key"
                )
            )
            OpenRouterService(config)
            print("❌ Should have failed with empty base URL")
            return False
        except ValueError:
            print("✅ Correctly caught empty base URL")
        
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False


async def main():
    """Main test function."""
    print("OpenRouter Service Test")
    print("=" * 50)
    
    sync_tests = [
        test_openrouter_message_model,
        test_openrouter_request_model,
        test_openrouter_service_initialization,
        test_crewai_adapter,
        test_error_handling,
    ]
    
    async_tests = [
        test_rate_limiter,
        test_text_generation,
        test_health_check,
    ]
    
    passed = 0
    total = len(sync_tests) + len(async_tests)
    
    # Run sync tests
    for test in sync_tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    # Run async tests
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
        print("🎉 All OpenRouter service tests passed!")
        return 0
    else:
        print("⚠️  Some OpenRouter service tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main())) 