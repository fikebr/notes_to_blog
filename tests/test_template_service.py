#!/usr/bin/env python3
"""
Test script to verify the template service works correctly.
"""

import sys
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.template_service import TemplateService
from src.models.blog_models import FrontMatter, BlogPost, Subheading


def test_template_service_initialization():
    """Test template service initialization."""
    print("Testing Template Service Initialization...")
    print("=" * 50)
    
    try:
        templates_dir = Path("templates")
        service = TemplateService(templates_dir)
        print(f"✅ Template service initialized with directory: {templates_dir}")
        
        # Test listing templates
        templates = service.list_available_templates()
        print(f"✅ Available templates: {templates}")
        
        return True
        
    except Exception as e:
        print(f"❌ Template service initialization failed: {e}")
        return False


def test_frontmatter_rendering():
    """Test frontmatter template rendering."""
    print("\nTesting Frontmatter Rendering...")
    print("=" * 50)
    
    try:
        service = TemplateService(Path("templates"))
        
        # Create test frontmatter
        frontmatter = FrontMatter(
            title="Test Blog Post",
            description="This is a test blog post description for testing purposes",
            categories=["development", "testing"],
            tags=["python", "testing", "templates"]
        )
        
        # Render frontmatter
        rendered = service.render_frontmatter(frontmatter)
        print(f"✅ Frontmatter rendered successfully")
        print(f"Rendered content length: {len(rendered)} characters")
        
        # Check for expected content
        if "title = \"Test Blog Post\"" in rendered:
            print("✅ Title correctly rendered")
        else:
            print("❌ Title not found in rendered content")
            return False
        
        if "categories = [\"development\", \"testing\"]" in rendered:
            print("✅ Categories correctly rendered")
        else:
            print("❌ Categories not found in rendered content")
            return False
        
        if "tags = [\"python\", \"testing\", \"templates\"]" in rendered:
            print("✅ Tags correctly rendered")
        else:
            print("❌ Tags not found in rendered content")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Frontmatter rendering failed: {e}")
        return False


def test_blog_post_rendering():
    """Test complete blog post template rendering."""
    print("\nTesting Blog Post Rendering...")
    print("=" * 50)
    
    try:
        service = TemplateService(Path("templates"))
        
        # Create test components
        frontmatter = FrontMatter(
            title="Complete Test Blog Post",
            description="A comprehensive test blog post with multiple sections",
            categories=["development"],
            tags=["python", "testing", "blogging"]
        )
        
        subheading1 = Subheading(
            title="First Section",
            content="This is the content of the first section with detailed information.",
            order=1
        )
        
        subheading2 = Subheading(
            title="Second Section",
            content="This is the content of the second section with more details and examples.",
            order=2
        )
        
        blog_post = BlogPost(
            frontmatter=frontmatter,
            content="Main content of the blog post with comprehensive information about the topic. This includes detailed explanations, examples, and practical applications that provide value to readers.",
            subheadings=[subheading1, subheading2],
            introduction="Welcome to this comprehensive test blog post. We will explore various aspects and provide detailed information throughout this article.",
            conclusion="Thank you for reading this test blog post. We hope you found the information valuable and informative for your needs.",
            filename="test-blog-post.md",
            output_path=Path("./output/test-blog-post.md")
        )
        
        # Render blog post
        rendered = service.render_blog_post(blog_post)
        print(f"✅ Blog post rendered successfully")
        print(f"Rendered content length: {len(rendered)} characters")
        
        # Check for expected content
        if "title = \"Complete Test Blog Post\"" in rendered:
            print("✅ Blog post title correctly rendered")
        else:
            print("❌ Blog post title not found in rendered content")
            return False
        
        if "## First Section" in rendered:
            print("✅ First subheading correctly rendered")
        else:
            print("❌ First subheading not found in rendered content")
            return False
        
        if "## Second Section" in rendered:
            print("✅ Second subheading correctly rendered")
        else:
            print("❌ Second subheading not found in rendered content")
            return False
        
        if "Welcome to this comprehensive test blog post." in rendered:
            print("✅ Introduction correctly rendered")
        else:
            print("❌ Introduction not found in rendered content")
            return False
        
        if "Thank you for reading this test blog post." in rendered:
            print("✅ Conclusion correctly rendered")
        else:
            print("❌ Conclusion not found in rendered content")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Blog post rendering failed: {e}")
        return False


def test_image_prompt_templates():
    """Test image prompt template functionality."""
    print("\nTesting Image Prompt Templates...")
    print("=" * 50)
    
    try:
        service = TemplateService(Path("templates"))
        
        # Test technology category header prompt
        tech_prompt = service.get_image_prompt_template("technology", "header")
        print(f"✅ Technology header prompt: {tech_prompt[:50]}...")
        
        # Test business category header prompt
        business_prompt = service.get_image_prompt_template("business", "header")
        print(f"✅ Business header prompt: {business_prompt[:50]}...")
        
        # Test content prompt
        content_prompt = service.get_image_prompt_template("development", "content")
        print(f"✅ Content prompt: {content_prompt[:50]}...")
        
        # Test default prompt for unknown category
        default_prompt = service.get_image_prompt_template("unknown_category", "header")
        print(f"✅ Default prompt: {default_prompt[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Image prompt template test failed: {e}")
        return False


def test_template_validation():
    """Test template syntax validation."""
    print("\nTesting Template Validation...")
    print("=" * 50)
    
    try:
        service = TemplateService(Path("templates"))
        
        # Test validation of existing templates
        templates = service.list_available_templates()
        
        for template_name in templates:
            is_valid = service.validate_template_syntax(template_name)
            if is_valid:
                print(f"✅ Template syntax valid: {template_name}")
            else:
                print(f"❌ Template syntax invalid: {template_name}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Template validation test failed: {e}")
        return False


def test_template_info():
    """Test template information retrieval."""
    print("\nTesting Template Information...")
    print("=" * 50)
    
    try:
        service = TemplateService(Path("templates"))
        
        # Get info for frontmatter template
        info = service.get_template_info("frontmatter_template.md")
        print(f"✅ Template info retrieved: {info['name']}")
        print(f"   Path: {info['path']}")
        print(f"   Size: {info['size']} bytes")
        print(f"   Syntax valid: {info['syntax_valid']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Template info test failed: {e}")
        return False


def main():
    """Main test function."""
    print("Template Service Test")
    print("=" * 50)
    
    tests = [
        test_template_service_initialization,
        test_frontmatter_rendering,
        test_blog_post_rendering,
        test_image_prompt_templates,
        test_template_validation,
        test_template_info,
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
        print("🎉 All template service tests passed!")
        return 0
    else:
        print("⚠️  Some template service tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 