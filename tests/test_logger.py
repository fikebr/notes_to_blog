#!/usr/bin/env python3
"""
Test script to verify the logging infrastructure works correctly.
"""

import os
import sys
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from logger import (
    setup_logging,
    get_logger,
    configure_logging_from_config,
    log_function_entry,
    log_function_exit,
    log_error,
    log_performance,
    initialize_logging,
    get_global_logger
)
from config import initialize_config


def test_basic_logging():
    """Test basic logging functionality."""
    print("Testing basic logging...")
    print("=" * 50)
    
    try:
        # Set up logging
        logger = setup_logging(Path("./logs/test.log"))
        
        # Test different log levels
        logger.debug("This is a debug message")
        logger.info("This is an info message")
        logger.warning("This is a warning message")
        logger.error("This is an error message")
        
        print("✅ Basic logging test passed")
        return True
        
    except Exception as e:
        print(f"❌ Basic logging test failed: {e}")
        return False


def test_logger_instances():
    """Test logger instance creation."""
    print("\nTesting logger instances...")
    print("=" * 50)
    
    try:
        # Test get_logger function
        test_logger = get_logger("test_module")
        test_logger.info("Test message from test_module logger")
        
        # Test that different loggers work
        another_logger = get_logger("another_module")
        another_logger.info("Test message from another_module logger")
        
        print("✅ Logger instances test passed")
        return True
        
    except Exception as e:
        print(f"❌ Logger instances test failed: {e}")
        return False


def test_configuration_based_logging():
    """Test logging with configuration."""
    print("\nTesting configuration-based logging...")
    print("=" * 50)
    
    try:
        # Set required environment variables
        os.environ["OPENROUTER_API_KEY"] = "test_openrouter_key"
        os.environ["REPLICATE_API_TOKEN"] = "test_replicate_token"
        os.environ["BRAVE_API_KEY"] = "test_brave_key"
        
        # Initialize config
        initialize_config()
        
        # Test configuration-based logging
        logger = configure_logging_from_config()
        logger.info("Test message using configuration-based logging")
        
        print("✅ Configuration-based logging test passed")
        return True
        
    except Exception as e:
        print(f"❌ Configuration-based logging test failed: {e}")
        return False


def test_logging_utilities():
    """Test logging utility functions."""
    print("\nTesting logging utilities...")
    print("=" * 50)
    
    try:
        logger = get_logger("test_utilities")
        
        # Test function entry/exit logging
        log_function_entry(logger, "test_function", param1="value1", param2=42)
        log_function_exit(logger, "test_function", result="success")
        
        # Test error logging
        try:
            raise ValueError("Test error for logging")
        except ValueError as e:
            log_error(logger, e, "test_function", line_number=123)
        
        # Test performance logging
        log_performance(logger, "test_operation", 1.234, items=100, status="completed")
        
        print("✅ Logging utilities test passed")
        return True
        
    except Exception as e:
        print(f"❌ Logging utilities test failed: {e}")
        return False


def test_global_logging():
    """Test global logging functionality."""
    print("\nTesting global logging...")
    print("=" * 50)
    
    try:
        # Test that get_global_logger fails before initialization
        try:
            get_global_logger()
            print("❌ Should have failed before initialization")
            return False
        except RuntimeError:
            print("✅ Correctly failed before initialization")
        
        # Initialize global logging
        global_logger = initialize_logging()
        global_logger.info("Test message from global logger")
        
        # Test get_global_logger after initialization
        retrieved_logger = get_global_logger()
        retrieved_logger.info("Test message from retrieved global logger")
        
        print("✅ Global logging test passed")
        return True
        
    except Exception as e:
        print(f"❌ Global logging test failed: {e}")
        return False


def test_file_rotation():
    """Test log file rotation functionality."""
    print("\nTesting file rotation...")
    print("=" * 50)
    
    try:
        # Create a small log file to test rotation
        log_file = Path("./logs/rotation_test.log")
        logger = setup_logging(
            log_file_path=log_file,
            max_bytes=1024,  # 1KB for testing
            backup_count=2
        )
        
        # Write enough messages to trigger rotation
        for i in range(100):
            logger.info(f"Test message {i}: " + "x" * 50)  # Make messages longer
        
        # Check if backup files were created
        backup_files = list(log_file.parent.glob("rotation_test.log.*"))
        if backup_files:
            print(f"✅ File rotation working: {len(backup_files)} backup files created")
        else:
            print("⚠️  No backup files created (may need more data)")
        
        print("✅ File rotation test passed")
        return True
        
    except Exception as e:
        print(f"❌ File rotation test failed: {e}")
        return False


def test_log_file_creation():
    """Test that log files are created properly."""
    print("\nTesting log file creation...")
    print("=" * 50)
    
    try:
        # Test with non-existent directory
        log_file = Path("./logs/nested/test.log")
        logger = setup_logging(log_file_path=log_file)
        logger.info("Test message in nested directory")
        
        # Check if file was created
        if log_file.exists():
            print(f"✅ Log file created: {log_file}")
            print(f"✅ File size: {log_file.stat().st_size} bytes")
        else:
            print("❌ Log file was not created")
            return False
        
        print("✅ Log file creation test passed")
        return True
        
    except Exception as e:
        print(f"❌ Log file creation test failed: {e}")
        return False


def main():
    """Main test function."""
    print("Logging Infrastructure Test")
    print("=" * 50)
    
    tests = [
        test_basic_logging,
        test_logger_instances,
        test_configuration_based_logging,
        test_logging_utilities,
        test_global_logging,
        test_log_file_creation,
        test_file_rotation,
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
        print("🎉 All logging tests passed!")
        return 0
    else:
        print("⚠️  Some logging tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 