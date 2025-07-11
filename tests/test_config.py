#!/usr/bin/env python3
"""
Test script to verify the refactored configuration system works correctly.
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.models.config_models import Config, APIConfig, AppConfig


def test_imports():
    """Test that all imports work correctly."""
    print("Testing imports...")
    print("=" * 50)
    
    try:
        # Test config module imports
        from config import load_config, initialize_config, get_config
        print("✅ config module imports work")
        
        # Test models imports
        from src.models.config_models import Config, APIConfig, AppConfig, PathConfig, LoggingConfig
        print("✅ models module imports work")
        
        # Test specific model imports
        from models.config_models import ContentConfig, ImageConfig, QualityConfig
        print("✅ specific model imports work")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False


def test_configuration_functionality():
    """Test that configuration functionality still works."""
    print("\nTesting configuration functionality...")
    print("=" * 50)
    
    # Set required environment variables for testing
    os.environ["OPENROUTER_API_KEY"] = "test_openrouter_key"
    os.environ["REPLICATE_API_TOKEN"] = "test_replicate_token"
    os.environ["BRAVE_API_KEY"] = "test_brave_key"
    
    try:
        config = load_config()
        
        # Test basic functionality
        print(f"✅ App Name: {config.app.app_name}")
        print(f"✅ API Key: {config.api.openrouter_api_key[:10]}...")
        print(f"✅ Inbox Dir: {config.paths.inbox_dir}")
        
        # Test global configuration
        initialize_config()
        global_config = get_config()
        print(f"✅ Global Config: {global_config.app.app_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration functionality test failed: {e}")
        return False


def test_model_validation():
    """Test that model validation still works."""
    print("\nTesting model validation...")
    print("=" * 50)
    
    try:
        # Test API config validation
        api_config = APIConfig(
            openrouter_api_key="test_key",
            replicate_api_token="test_token",
            brave_api_key="test_brave_key"
        )
        print("✅ API config validation works")
        
        # Test app config validation
        app_config = AppConfig(
            app_name="Test App",
            app_version="1.0.0",
            app_env="testing",
            debug=True
        )
        print("✅ App config validation works")
        
        return True
        
    except Exception as e:
        print(f"❌ Model validation test failed: {e}")
        return False


def main():
    """Main test function."""
    print("Refactored Configuration System Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_configuration_functionality,
        test_model_validation,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All refactored configuration tests passed!")
        return 0
    else:
        print("⚠️  Some refactored configuration tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 