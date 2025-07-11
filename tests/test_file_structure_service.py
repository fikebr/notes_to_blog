#!/usr/bin/env python3
"""
Test script to verify the file structure service works correctly.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.file_structure_service import FileStructureService


def test_file_structure_service_initialization():
    """Test file structure service initialization."""
    print("Testing File Structure Service Initialization...")
    print("=" * 50)
    
    try:
        base_path = Path(".")
        service = FileStructureService(base_path)
        print(f"✅ File structure service initialized with base path: {base_path}")
        
        # Check that directories are defined
        expected_dirs = ["inbox", "output", "images", "templates", "logs"]
        for dir_name in expected_dirs:
            if dir_name in service.directories:
                print(f"✅ Directory {dir_name} configured: {service.directories[dir_name]}")
            else:
                print(f"❌ Directory {dir_name} not configured")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ File structure service initialization failed: {e}")
        return False


def test_directory_creation():
    """Test directory creation functionality."""
    print("\nTesting Directory Creation...")
    print("=" * 50)
    
    try:
        service = FileStructureService(Path("."))
        
        # Create directory structure
        results = service.create_directory_structure()
        print(f"✅ Directory creation results: {results}")
        
        # Check that all directories were created successfully
        for dir_name, success in results.items():
            if success:
                print(f"✅ Directory {dir_name} created successfully")
            else:
                print(f"❌ Failed to create directory {dir_name}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Directory creation test failed: {e}")
        return False


def test_directory_validation():
    """Test directory validation functionality."""
    print("\nTesting Directory Validation...")
    print("=" * 50)
    
    try:
        service = FileStructureService(Path("."))
        
        # Validate directory structure
        validation_results = service.validate_directory_structure()
        print(f"✅ Validation results: {validation_results}")
        
        # Check that all directories are valid
        for dir_name, validation in validation_results.items():
            if validation["exists"] and validation["is_directory"]:
                print(f"✅ Directory {dir_name} is valid")
            else:
                print(f"❌ Directory {dir_name} is invalid: {validation}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Directory validation test failed: {e}")
        return False


def test_directory_info():
    """Test directory information retrieval."""
    print("\nTesting Directory Information...")
    print("=" * 50)
    
    try:
        service = FileStructureService(Path("."))
        
        # Get info for each directory
        for dir_name in ["inbox", "output", "images"]:
            info = service.get_directory_info(dir_name)
            print(f"✅ Directory info for {dir_name}:")
            print(f"   Path: {info['path']}")
            print(f"   Exists: {info['exists']}")
            print(f"   File count: {info.get('file_count', 0)}")
            print(f"   Total size: {info.get('total_size', 0)} bytes")
            
            if not info["exists"]:
                print(f"❌ Directory {dir_name} does not exist")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Directory info test failed: {e}")
        return False


def test_directory_contents():
    """Test directory contents listing."""
    print("\nTesting Directory Contents...")
    print("=" * 50)
    
    try:
        service = FileStructureService(Path("."))
        
        # List contents of inbox directory
        inbox_contents = service.list_directory_contents("inbox")
        print(f"✅ Inbox contents: {len(inbox_contents)} items")
        
        for item in inbox_contents:
            print(f"   - {item['name']} ({'file' if item['is_file'] else 'directory'})")
        
        # List contents of output directory
        output_contents = service.list_directory_contents("output")
        print(f"✅ Output contents: {len(output_contents)} items")
        
        for item in output_contents:
            print(f"   - {item['name']} ({'file' if item['is_file'] else 'directory'})")
        
        return True
        
    except Exception as e:
        print(f"❌ Directory contents test failed: {e}")
        return False


def test_storage_usage():
    """Test storage usage calculation."""
    print("\nTesting Storage Usage...")
    print("=" * 50)
    
    try:
        service = FileStructureService(Path("."))
        
        # Get storage usage
        usage = service.get_storage_usage()
        print(f"✅ Storage usage: {usage['total_size']} bytes total")
        print(f"✅ Total files: {usage['total_files']}")
        
        for dir_name, dir_usage in usage["directory_usage"].items():
            print(f"   {dir_name}: {dir_usage['size']} bytes, {dir_usage['file_count']} files")
        
        return True
        
    except Exception as e:
        print(f"❌ Storage usage test failed: {e}")
        return False


def test_cleanup_functionality():
    """Test directory cleanup functionality."""
    print("\nTesting Cleanup Functionality...")
    print("=" * 50)
    
    try:
        service = FileStructureService(Path("."))
        
        # Test cleanup (should not remove any files since they're new)
        cleanup_results = service.cleanup_directory("inbox", max_age_days=1)
        print(f"✅ Cleanup results: {cleanup_results}")
        
        if cleanup_results["files_checked"] >= 0:
            print(f"✅ Cleanup checked {cleanup_results['files_checked']} files")
        else:
            print(f"❌ Cleanup failed to check files")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Cleanup test failed: {e}")
        return False


def test_error_handling():
    """Test error handling for invalid operations."""
    print("\nTesting Error Handling...")
    print("=" * 50)
    
    try:
        service = FileStructureService(Path("."))
        
        # Test invalid directory name
        try:
            service.get_directory_info("invalid_directory")
            print("❌ Should have raised ValueError for invalid directory")
            return False
        except ValueError:
            print("✅ Correctly caught invalid directory name")
        
        # Test invalid directory name for listing
        try:
            service.list_directory_contents("invalid_directory")
            print("❌ Should have raised ValueError for invalid directory")
            return False
        except ValueError:
            print("✅ Correctly caught invalid directory name for listing")
        
        # Test invalid directory name for cleanup
        try:
            service.cleanup_directory("invalid_directory")
            print("❌ Should have raised ValueError for invalid directory")
            return False
        except ValueError:
            print("✅ Correctly caught invalid directory name for cleanup")
        
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False


def main():
    """Main test function."""
    print("File Structure Service Test")
    print("=" * 50)
    
    tests = [
        test_file_structure_service_initialization,
        test_directory_creation,
        test_directory_validation,
        test_directory_info,
        test_directory_contents,
        test_storage_usage,
        test_cleanup_functionality,
        test_error_handling,
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
        print("🎉 All file structure service tests passed!")
        return 0
    else:
        print("⚠️  Some file structure service tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 