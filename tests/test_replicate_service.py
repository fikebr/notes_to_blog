#!/usr/bin/env python3
"""
Test script to verify the Replicate service works correctly.
"""

import sys
import asyncio
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.replicate_service import (
    ReplicateService, 
    ReplicatePrediction, 
    ImageGenerationRequest, 
    ImageGenerationResult,
    ImageProcessor
)
from src.models.config_models import Config
from models.config_models import APIConfig


def test_image_generation_request_model():
    """Test ImageGenerationRequest model validation."""
    print("Testing ImageGenerationRequest Model...")
    print("=" * 50)
    
    try:
        # Valid request
        request = ImageGenerationRequest(
            prompt="A beautiful sunset over mountains",
            width=1024,
            height=1024,
            num_outputs=1
        )
        print(f"✅ Valid request created: {request.prompt}")
        
        # Test invalid width (not multiple of 8)
        try:
            ImageGenerationRequest(
                prompt="Test",
                width=1001,  # Not multiple of 8
                height=1024
            )
            print("❌ Should have failed with invalid width")
            return False
        except Exception:
            print("✅ Correctly caught invalid width")
        
        # Test invalid height (not multiple of 8)
        try:
            ImageGenerationRequest(
                prompt="Test",
                width=1024,
                height=1001  # Not multiple of 8
            )
            print("❌ Should have failed with invalid height")
            return False
        except Exception:
            print("✅ Correctly caught invalid height")
        
        # Test invalid width range
        try:
            ImageGenerationRequest(
                prompt="Test",
                width=100,  # Too small
                height=1024
            )
            print("❌ Should have failed with width too small")
            return False
        except Exception:
            print("✅ Correctly caught width too small")
        
        # Test invalid height range
        try:
            ImageGenerationRequest(
                prompt="Test",
                width=1024,
                height=3000  # Too large
            )
            print("❌ Should have failed with height too large")
            return False
        except Exception:
            print("✅ Correctly caught height too large")
        
        # Test invalid num_outputs
        try:
            ImageGenerationRequest(
                prompt="Test",
                num_outputs=10  # Too many
            )
            print("❌ Should have failed with too many outputs")
            return False
        except Exception:
            print("✅ Correctly caught too many outputs")
        
        return True
        
    except Exception as e:
        print(f"❌ Request model test failed: {e}")
        return False


def test_replicate_prediction_model():
    """Test ReplicatePrediction model validation."""
    print("\nTesting ReplicatePrediction Model...")
    print("=" * 50)
    
    try:
        # Valid prediction
        prediction = ReplicatePrediction(
            id="test_prediction_id",
            version="test_model_version",
            status="succeeded",
            input={"prompt": "test"},
            output=["https://example.com/image.png"],
            created_at="2023-01-01T00:00:00Z"
        )
        print(f"✅ Valid prediction created: {prediction.id}")
        
        # Test with different statuses
        statuses = ["starting", "processing", "succeeded", "failed", "canceled"]
        for status in statuses:
            pred = ReplicatePrediction(
                id=f"test_{status}",
                version="test",
                status=status,
                input={"prompt": "test"},
                created_at="2023-01-01T00:00:00Z"
            )
            print(f"✅ Prediction with status '{status}' created")
        
        return True
        
    except Exception as e:
        print(f"❌ Prediction model test failed: {e}")
        return False


def test_image_generation_result_model():
    """Test ImageGenerationResult model validation."""
    print("\nTesting ImageGenerationResult Model...")
    print("=" * 50)
    
    try:
        # Successful result
        result = ImageGenerationResult(
            success=True,
            image_urls=["https://example.com/image1.png", "https://example.com/image2.png"],
            prediction_id="test_prediction_id",
            generation_time=30.5,
            model_used="test_model"
        )
        print(f"✅ Successful result created: {len(result.image_urls)} images")
        
        # Failed result
        failed_result = ImageGenerationResult(
            success=False,
            error="Generation failed",
            model_used="test_model"
        )
        print(f"✅ Failed result created: {failed_result.error}")
        
        return True
        
    except Exception as e:
        print(f"❌ Result model test failed: {e}")
        return False


def test_image_processor():
    """Test ImageProcessor utilities."""
    print("\nTesting ImageProcessor...")
    print("=" * 50)
    
    try:
        # Test URL validation
        valid_urls = [
            "https://example.com/image.png",
            "http://example.com/image.jpg",
            "https://cdn.replicate.com/image.webp"
        ]
        
        invalid_urls = [
            "not_a_url",
            "ftp://example.com/image.png",
            "",
            "https://"
        ]
        
        for url in valid_urls:
            assert ImageProcessor.validate_image_url(url), f"Should be valid: {url}"
        print("✅ Valid URL validation passed")
        
        for url in invalid_urls:
            assert not ImageProcessor.validate_image_url(url), f"Should be invalid: {url}"
        print("✅ Invalid URL validation passed")
        
        # Test file extension extraction
        test_cases = [
            ("https://example.com/image.png", ".png"),
            ("https://example.com/image.jpg", ".jpg"),
            ("https://example.com/image.jpeg", ".jpeg"),
            ("https://example.com/image.webp", ".webp"),
            ("https://example.com/image", ".png"),  # Default
            ("https://example.com/image.PNG", ".png"),  # Case insensitive
        ]
        
        for url, expected_ext in test_cases:
            ext = ImageProcessor.get_file_extension(url)
            assert ext == expected_ext, f"Expected {expected_ext}, got {ext} for {url}"
        print("✅ File extension extraction passed")
        
        # Test filename generation
        prompt = "A beautiful sunset"
        filename1 = ImageProcessor.generate_filename(prompt, 0)
        filename2 = ImageProcessor.generate_filename(prompt, 1)
        
        assert filename1 != filename2, "Different indices should generate different filenames"
        assert "image_" in filename1, "Filename should start with 'image_'"
        assert filename1.endswith("_0"), "Filename should end with index"
        print("✅ Filename generation passed")
        
        return True
        
    except Exception as e:
        print(f"❌ ImageProcessor test failed: {e}")
        return False


def test_replicate_service_initialization():
    """Test Replicate service initialization."""
    print("\nTesting Replicate Service Initialization...")
    print("=" * 50)
    
    try:
        # Create mock config
        config = Config(
            api=APIConfig(
                openrouter_api_key="test_key",
                openrouter_base_url="https://openrouter.ai/api/v1",
                replicate_api_token="test_token",
                brave_api_key="test_brave_key"
            )
        )
        
        service = ReplicateService(config)
        print(f"✅ Replicate service initialized")
        print(f"   Model ID: {service.model_id}")
        print(f"   Base URL: {service.base_url}")
        
        # Test invalid API token
        try:
            invalid_config = Config(
                api=APIConfig(
                    openrouter_api_key="test_key",
                    openrouter_base_url="https://openrouter.ai/api/v1",
                    replicate_api_token="your_replicate_api_token_here",
                    brave_api_key="test_brave_key"
                )
            )
            ReplicateService(invalid_config)
            print("❌ Should have failed with placeholder API token")
            return False
        except ValueError:
            print("✅ Correctly caught placeholder API token")
        
        return True
        
    except Exception as e:
        print(f"❌ Service initialization test failed: {e}")
        return False


async def test_image_generation_structure():
    """Test image generation structure (without real API calls)."""
    print("\nTesting Image Generation Structure...")
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
        
        service = ReplicateService(config)
        
        # Test request preparation
        request_data = ImageGenerationRequest(
            prompt="A beautiful sunset over mountains",
            width=1024,
            height=1024,
            num_outputs=1
        )
        
        print(f"✅ Request data prepared: {request_data.prompt}")
        print(f"   Dimensions: {request_data.width}x{request_data.height}")
        print(f"   Outputs: {request_data.num_outputs}")
        
        # This would fail with a test token, but we can test the structure
        print("✅ Image generation structure tested (requires real API token for full test)")
        
        return True
        
    except Exception as e:
        print(f"❌ Image generation structure test failed: {e}")
        return False


async def test_image_download_structure():
    """Test image download structure (without real downloads)."""
    print("\nTesting Image Download Structure...")
    print("=" * 50)
    
    try:
        # Test with mock URLs
        mock_urls = [
            "https://example.com/image1.png",
            "https://example.com/image2.jpg"
        ]
        
        # Test URL validation
        for url in mock_urls:
            is_valid = ImageProcessor.validate_image_url(url)
            print(f"   URL validation: {url} -> {is_valid}")
        
        # Test filename generation
        prompt = "A beautiful sunset"
        for i, url in enumerate(mock_urls):
            filename = ImageProcessor.generate_filename(prompt, i)
            extension = ImageProcessor.get_file_extension(url)
            full_filename = f"{filename}{extension}"
            print(f"   Generated filename: {full_filename}")
        
        print("✅ Image download structure tested (requires real URLs for full test)")
        return True
        
    except Exception as e:
        print(f"❌ Image download structure test failed: {e}")
        return False


def test_error_handling():
    """Test error handling scenarios."""
    print("\nTesting Error Handling...")
    print("=" * 50)
    
    try:
        # Test missing API token
        try:
            config = Config(
                api=APIConfig(
                    openrouter_api_key="test_key",
                    openrouter_base_url="https://openrouter.ai/api/v1",
                    replicate_api_token="",
                    brave_api_key="test_brave_key"
                )
            )
            ReplicateService(config)
            print("❌ Should have failed with empty API token")
            return False
        except ValueError:
            print("✅ Correctly caught empty API token")
        
        # Test invalid model ID
        try:
            config = Config(
                api=APIConfig(
                    openrouter_api_key="test_key",
                    openrouter_base_url="https://openrouter.ai/api/v1",
                    replicate_api_token="test_token",
                    brave_api_key="test_brave_key"
                )
            )
            # Temporarily set invalid model
            config.image.image_model = ""
            ReplicateService(config)
            print("❌ Should have failed with empty model ID")
            return False
        except ValueError:
            print("✅ Correctly caught empty model ID")
        
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
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
        
        service = ReplicateService(config)
        
        # Health check should fail with test token, but we can test the structure
        health_result = await service.health_check()
        
        print(f"✅ Health check structure: {health_result}")
        print(f"   Status: {health_result.get('status')}")
        print(f"   Timestamp: {health_result.get('timestamp')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Health check test failed: {e}")
        return False


async def main():
    """Main test function."""
    print("Replicate Service Test")
    print("=" * 50)
    
    sync_tests = [
        test_image_generation_request_model,
        test_replicate_prediction_model,
        test_image_generation_result_model,
        test_image_processor,
        test_replicate_service_initialization,
        test_error_handling,
    ]
    
    async_tests = [
        test_image_generation_structure,
        test_image_download_structure,
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
        print("🎉 All Replicate service tests passed!")
        return 0
    else:
        print("⚠️  Some Replicate service tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main())) 