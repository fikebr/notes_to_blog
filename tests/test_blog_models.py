#!/usr/bin/env python3
"""
Test script to verify the blog models work correctly.
"""

import sys
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models import (
    Category,
    Tag,
    Image,
    FrontMatter,
    Note,
    Subheading,
    BlogPost
)


def test_category_model():
    """Test Category model validation."""
    print("Testing Category model...")
    print("=" * 50)
    
    try:
        # Valid category
        category = Category(
            name="Development",
            slug="development",
            description="Software development topics"
        )
        print(f"✅ Valid category: {category.name}")
        
        # Test slug validation
        category2 = Category(
            name="Web Development",
            slug="web-development",
            description="Web development topics"
        )
        print(f"✅ Valid slug with hyphens: {category2.slug}")
        
        # Test invalid slug
        try:
            Category(
                name="Invalid",
                slug="invalid slug!",
                description="Invalid slug"
            )
            print("❌ Should have failed with invalid slug")
            return False
        except ValueError:
            print("✅ Correctly caught invalid slug")
        
        return True
        
    except Exception as e:
        print(f"❌ Category test failed: {e}")
        return False


def test_tag_model():
    """Test Tag model validation."""
    print("\nTesting Tag model...")
    print("=" * 50)
    
    try:
        # Valid tag
        tag = Tag(name="Python", slug="python")
        print(f"✅ Valid tag: {tag.name}")
        
        # Test slug validation
        tag2 = Tag(name="Machine Learning", slug="machine_learning")
        print(f"✅ Valid slug with underscores: {tag2.slug}")
        
        # Test invalid slug
        try:
            Tag(name="Invalid", slug="invalid tag!")
            print("❌ Should have failed with invalid slug")
            return False
        except ValueError:
            print("✅ Correctly caught invalid slug")
        
        return True
        
    except Exception as e:
        print(f"❌ Tag test failed: {e}")
        return False


def test_image_model():
    """Test Image model validation."""
    print("\nTesting Image model...")
    print("=" * 50)
    
    try:
        # Valid image
        image = Image(
            filename="test-image.jpg",
            file_path=Path("./images/test-image.jpg"),
            prompt="A beautiful landscape with mountains",
            alt_text="Mountain landscape",
            width=1024,
            height=768,
            model_used="stability-ai/sdxl"
        )
        print(f"✅ Valid image: {image.filename}")
        
        # Test invalid filename
        try:
            Image(
                filename="test-image.txt",
                file_path=Path("./images/test-image.txt"),
                prompt="Test prompt",
                alt_text="Test alt",
                width=1024,
                height=768,
                model_used="test-model"
            )
            print("❌ Should have failed with invalid filename")
            return False
        except ValueError:
            print("✅ Correctly caught invalid filename")
        
        # Test invalid dimensions
        try:
            Image(
                filename="test-image.jpg",
                file_path=Path("./images/test-image.jpg"),
                prompt="Test prompt",
                alt_text="Test alt",
                width=100,  # Too small
                height=768,
                model_used="test-model"
            )
            print("❌ Should have failed with invalid dimensions")
            return False
        except ValueError:
            print("✅ Correctly caught invalid dimensions")
        
        return True
        
    except Exception as e:
        print(f"❌ Image test failed: {e}")
        return False


def test_frontmatter_model():
    """Test FrontMatter model validation."""
    print("\nTesting FrontMatter model...")
    print("=" * 50)
    
    try:
        # Valid frontmatter
        frontmatter = FrontMatter(
            title="My First Blog Post",
            description="This is a comprehensive guide to getting started with blogging",
            categories=["development", "tutorial"],
            tags=["python", "blogging", "guide"]
        )
        print(f"✅ Valid frontmatter: {frontmatter.title}")
        
        # Test invalid title
        try:
            FrontMatter(
                title="Hi",  # Too short
                description="Valid description",
                categories=["development"],
                tags=["python", "blogging"]
            )
            print("❌ Should have failed with short title")
            return False
        except ValueError:
            print("✅ Correctly caught short title")
        
        # Test invalid categories
        try:
            FrontMatter(
                title="Valid Title",
                description="Valid description",
                categories=[],  # Empty
                tags=["python", "blogging"]
            )
            print("❌ Should have failed with empty categories")
            return False
        except ValueError:
            print("✅ Correctly caught empty categories")
        
        # Test invalid tags
        try:
            FrontMatter(
                title="Valid Title",
                description="Valid description",
                categories=["development"],
                tags=["python"]  # Too few
            )
            print("❌ Should have failed with too few tags")
            return False
        except ValueError:
            print("✅ Correctly caught too few tags")
        
        return True
        
    except Exception as e:
        print(f"❌ FrontMatter test failed: {e}")
        return False


def test_note_model():
    """Test Note model validation."""
    print("\nTesting Note model...")
    print("=" * 50)
    
    try:
        # Valid note
        note = Note(
            content="This is a comprehensive note about Python programming with lots of details and examples.",
            title="Python Programming Notes"
        )
        print(f"✅ Valid note: {note.title}")
        
        # Test invalid content
        try:
            Note(content="Short")  # Too short
            print("❌ Should have failed with short content")
            return False
        except ValueError:
            print("✅ Correctly caught short content")
        
        # Test invalid title
        try:
            Note(
                content="Valid content with sufficient length",
                title="Hi"  # Too short
            )
            print("❌ Should have failed with short title")
            return False
        except ValueError:
            print("✅ Correctly caught short title")
        
        return True
        
    except Exception as e:
        print(f"❌ Note test failed: {e}")
        return False


def test_subheading_model():
    """Test Subheading model validation."""
    print("\nTesting Subheading model...")
    print("=" * 50)
    
    try:
        # Valid subheading
        subheading = Subheading(
            title="Getting Started",
            content="This section covers the basics of getting started with the topic. It provides a comprehensive overview and step-by-step instructions.",
            order=1
        )
        print(f"✅ Valid subheading: {subheading.title}")
        
        # Test invalid title
        try:
            Subheading(
                title="Hi",  # Too short
                content="Valid content with sufficient length",
                order=1
            )
            print("❌ Should have failed with short title")
            return False
        except ValueError:
            print("✅ Correctly caught short title")
        
        # Test invalid content
        try:
            Subheading(
                title="Valid Title",
                content="Short",  # Too short
                order=1
            )
            print("❌ Should have failed with short content")
            return False
        except ValueError:
            print("✅ Correctly caught short content")
        
        return True
        
    except Exception as e:
        print(f"❌ Subheading test failed: {e}")
        return False


def test_blog_post_model():
    """Test BlogPost model validation and functionality."""
    print("\nTesting BlogPost model...")
    print("=" * 50)
    
    try:
        # Create valid components
        frontmatter = FrontMatter(
            title="Complete Guide to Python Blogging",
            description="A comprehensive guide to creating blog posts with Python and AI assistance",
            categories=["development", "tutorial"],
            tags=["python", "blogging", "ai", "guide"]
        )
        
        subheading1 = Subheading(
            title="Introduction to Python",
            content="Python is a versatile programming language that's perfect for beginners and experts alike. This section covers the fundamentals.",
            order=1
        )
        
        subheading2 = Subheading(
            title="Advanced Features",
            content="Once you've mastered the basics, you can explore Python's advanced features like decorators, generators, and context managers.",
            order=2
        )
        
        # Valid blog post
        blog_post = BlogPost(
            frontmatter=frontmatter,
            content="This is a comprehensive blog post about Python programming with detailed explanations and practical examples.",
            subheadings=[subheading1, subheading2],
            introduction="Welcome to this comprehensive guide on Python programming. We'll cover everything from basics to advanced topics.",
            conclusion="In conclusion, Python is an excellent language for both beginners and experienced developers. Keep practicing and exploring!",
            filename="python-guide.md",
            output_path=Path("./output/python-guide.md")
        )
        
        print(f"✅ Valid blog post: {blog_post.frontmatter.title}")
        
        # Test word count calculation
        word_count = blog_post.calculate_word_count()
        print(f"✅ Word count calculated: {word_count} words")
        
        # Test reading time calculation
        reading_time = blog_post.calculate_reading_time()
        print(f"✅ Reading time calculated: {reading_time} minutes")
        
        # Test markdown conversion
        markdown = blog_post.to_markdown()
        print(f"✅ Markdown generated: {len(markdown)} characters")
        
        # Test invalid filename
        try:
            BlogPost(
                frontmatter=frontmatter,
                content="Valid content",
                subheadings=[subheading1, subheading2],
                introduction="Valid introduction",
                conclusion="Valid conclusion",
                filename="test.txt",  # Wrong extension
                output_path=Path("./output/test.txt")
            )
            print("❌ Should have failed with wrong file extension")
            return False
        except ValueError:
            print("✅ Correctly caught wrong file extension")
        
        # Test invalid subheadings order
        try:
            BlogPost(
                frontmatter=frontmatter,
                content="Valid content",
                subheadings=[subheading2, subheading1],  # Wrong order
                introduction="Valid introduction",
                conclusion="Valid conclusion",
                filename="test.md",
                output_path=Path("./output/test.md")
            )
            print("❌ Should have failed with wrong subheading order")
            return False
        except ValueError:
            print("✅ Correctly caught wrong subheading order")
        
        return True
        
    except Exception as e:
        print(f"❌ BlogPost test failed: {e}")
        return False


def main():
    """Main test function."""
    print("Blog Models Test")
    print("=" * 50)
    
    tests = [
        test_category_model,
        test_tag_model,
        test_image_model,
        test_frontmatter_model,
        test_note_model,
        test_subheading_model,
        test_blog_post_model,
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
        print("🎉 All blog model tests passed!")
        return 0
    else:
        print("⚠️  Some blog model tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 