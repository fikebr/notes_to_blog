"""
Unit tests for Pydantic models.
"""
import pytest
from datetime import datetime
from pathlib import Path

from src.models.config_models import (
    Config, APIConfig, AppConfig, ImageConfig, 
    LoggingConfig, PathConfig, ContentConfig
)
from src.models.blog_models import (
    BlogPost, Note, Image, Category, Tag, 
    FrontMatter, Subheading
)


class TestConfigModels:
    """Test configuration models."""
    
    def test_api_config_valid(self):
        """Test valid API configuration."""
        config = APIConfig(
            openrouter_api_key="test-key",
            openrouter_base_url="https://api.openrouter.ai/api/v1",
            replicate_api_token="test-key",
            brave_api_key="test-key",
            brave_search_url="https://api.search.brave.com/res/v1/web/search"
        )
        assert config.openrouter_api_key == "test-key"
        assert config.openrouter_base_url == "https://api.openrouter.ai/api/v1"
        assert config.replicate_api_token == "test-key"
        assert config.brave_api_key == "test-key"

    def test_app_config_valid(self):
        """Test valid App configuration."""
        config = AppConfig(
            app_name="test-app",
            app_version="0.1.0",
            app_env="test",
            debug=True
        )
        assert config.app_name == "test-app"
        assert config.app_version == "0.1.0"
        assert config.app_env == "test"
        assert config.debug is True

    def test_image_config_valid(self):
        """Test valid Image configuration."""
        config = ImageConfig(
            image_model="stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
            image_width=1024,
            image_height=1024,
            max_images_per_post=5
        )
        assert config.image_width == 1024
        assert config.image_height == 1024
        assert config.max_images_per_post == 5

    def test_image_config_invalid_dimensions(self):
        """Test invalid image dimensions."""
        with pytest.raises(ValueError):
            ImageConfig(
                image_model="stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
                image_width=100,  # Invalid: < 256
                image_height=1024,
                max_images_per_post=5
            )

    def test_logging_config_valid(self):
        """Test valid Logging configuration."""
        config = LoggingConfig(
            log_level="DEBUG",
            log_format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            log_max_size=10_485_760,
            log_backup_count=3
        )
        assert config.log_level == "DEBUG"
        assert config.log_max_size == 10_485_760
        assert config.log_backup_count == 3

    def test_path_config_valid(self):
        """Test valid Path configuration."""
        config = PathConfig(
            inbox_dir=Path("./inbox"),
            output_dir=Path("./output"),
            images_dir=Path("./images"),
            templates_dir=Path("./templates"),
            log_file=Path("./logs/app.log")
        )
        assert config.inbox_dir == Path("./inbox")
        assert config.output_dir == Path("./output")
        assert config.images_dir == Path("./images")

    def test_content_config_valid(self):
        """Test valid Content configuration."""
        config = ContentConfig(
            default_categories=["development", "ai", "business"],
            max_subheadings=5,
            min_subheadings=2,
            max_tags=5,
            min_tags=2
        )
        assert len(config.default_categories) == 3
        assert config.max_subheadings == 5
        assert config.min_subheadings == 2

    def test_main_config_valid(self, test_config):
        """Test valid main Config."""
        assert test_config.api.openrouter_api_key == "test-key"
        assert test_config.app.app_name == "test-app"
        assert test_config.logging.log_level == "DEBUG"
        assert test_config.image.image_width == 1024


class TestBlogModels:
    """Test blog-related models."""
    
    def test_note_valid(self):
        """Test valid Note model."""
        note = Note(
            content="Test note content",
            source_file="test.md",
            file_type="markdown"
        )
        assert note.content == "Test note content"
        assert note.source_file == "test.md"
        assert note.file_type == "markdown"
        assert note.created_at is not None

    def test_note_empty_content(self):
        """Test Note with empty content."""
        with pytest.raises(ValueError):
            Note(
                content="",
                source_file="test.md",
                file_type="markdown"
            )

    def test_image_valid(self):
        """Test valid Image model."""
        image = Image(
            url="https://example.com/image.jpg",
            alt_text="Test image",
            caption="A test image",
            local_path="/path/to/image.jpg"
        )
        assert image.url == "https://example.com/image.jpg"
        assert image.alt_text == "Test image"
        assert image.caption == "A test image"
        assert image.local_path == "/path/to/image.jpg"

    def test_category_valid(self):
        """Test valid Category model."""
        category = Category(name="development", display_name="Development")
        assert category.name == "development"
        assert category.display_name == "Development"

    def test_category_invalid_name(self):
        """Test invalid category name."""
        with pytest.raises(ValueError):
            Category(name="invalid-category", display_name="Invalid")

    def test_tag_valid(self):
        """Test valid Tag model."""
        tag = Tag(name="python", display_name="Python")
        assert tag.name == "python"
        assert tag.display_name == "Python"

    def test_subheading_valid(self):
        """Test valid Subheading model."""
        subheading = Subheading(
            title="Test Subheading",
            content="Test content",
            order=1
        )
        assert subheading.title == "Test Subheading"
        assert subheading.content == "Test content"
        assert subheading.order == 1

    def test_frontmatter_valid(self):
        """Test valid FrontMatter model."""
        frontmatter = FrontMatter(
            title="Test Post",
            description="Test description",
            date=datetime.now(),
            draft=True,
            category="development",
            tags=["test", "blog"]
        )
        assert frontmatter.title == "Test Post"
        assert frontmatter.description == "Test description"
        assert frontmatter.draft is True
        assert frontmatter.category == "development"
        assert frontmatter.tags == ["test", "blog"]

    def test_frontmatter_to_dict(self):
        """Test FrontMatter to_dict method."""
        frontmatter = FrontMatter(
            title="Test Post",
            description="Test description",
            date=datetime(2025, 1, 27),
            draft=True,
            category="development",
            tags=["test", "blog"]
        )
        data = frontmatter.to_dict()
        assert data["title"] == "Test Post"
        assert data["description"] == "Test description"
        assert data["draft"] is True
        assert data["taxonomies"]["categories"] == ["development"]
        assert data["taxonomies"]["tags"] == ["test", "blog"]

    def test_blog_post_valid(self):
        """Test valid BlogPost model."""
        blog_post = BlogPost(
            title="Test Blog Post",
            description="Test description",
            content="# Test Post\n\nContent here.",
            category="development",
            tags=["test", "blog"],
            images=[
                Image(
                    url="https://example.com/image.jpg",
                    alt_text="Test image",
                    caption="A test image"
                )
            ]
        )
        assert blog_post.title == "Test Blog Post"
        assert blog_post.description == "Test description"
        assert blog_post.content == "# Test Post\n\nContent here."
        assert blog_post.category == "development"
        assert len(blog_post.tags) == 2
        assert len(blog_post.images) == 1

    def test_blog_post_generate_filename(self):
        """Test BlogPost filename generation."""
        blog_post = BlogPost(
            title="Test Blog Post Title",
            description="Test description",
            content="# Test Post\n\nContent here.",
            category="development",
            tags=["test", "blog"]
        )
        filename = blog_post.generate_filename()
        assert filename.startswith("test-blog-post-title")
        assert filename.endswith(".md")

    def test_blog_post_to_markdown(self):
        """Test BlogPost to_markdown method."""
        blog_post = BlogPost(
            title="Test Blog Post",
            description="Test description",
            content="# Test Post\n\nContent here.",
            category="development",
            tags=["test", "blog"]
        )
        markdown = blog_post.to_markdown()
        assert "+++" in markdown
        assert "title = \"Test Blog Post\"" in markdown
        assert "# Test Post" in markdown

    def test_blog_post_validation_errors(self):
        """Test BlogPost validation errors."""
        with pytest.raises(ValueError):
            BlogPost(
                title="",  # Empty title
                description="Test description",
                content="# Test Post\n\nContent here.",
                category="development",
                tags=["test", "blog"]
            )

        with pytest.raises(ValueError):
            BlogPost(
                title="Test Post",
                description="Test description",
                content="# Test Post\n\nContent here.",
                category="invalid-category",  # Invalid category
                tags=["test", "blog"]
            )

        with pytest.raises(ValueError):
            BlogPost(
                title="Test Post",
                description="Test description",
                content="# Test Post\n\nContent here.",
                category="development",
                tags=["test"] * 10  # Too many tags
            )

    def test_blog_post_with_images(self):
        """Test BlogPost with images."""
        images = [
            Image(
                url="https://example.com/image1.jpg",
                alt_text="Image 1",
                caption="First image"
            ),
            Image(
                url="https://example.com/image2.jpg",
                alt_text="Image 2",
                caption="Second image"
            )
        ]
        
        blog_post = BlogPost(
            title="Test Post with Images",
            description="Test description",
            content="# Test Post\n\nContent with images.",
            category="development",
            tags=["test", "images"],
            images=images
        )
        
        assert len(blog_post.images) == 2
        assert blog_post.images[0].alt_text == "Image 1"
        assert blog_post.images[1].alt_text == "Image 2"

    def test_blog_post_word_count(self):
        """Test BlogPost word count calculation."""
        blog_post = BlogPost(
            title="Test Post",
            description="Test description",
            content="# Test Post\n\nThis is a test post with some content. It has multiple words.",
            category="development",
            tags=["test", "blog"]
        )
        
        # Should count words in content (excluding markdown)
        assert blog_post.word_count > 0
        assert isinstance(blog_post.word_count, int)

    def test_blog_post_reading_time(self):
        """Test BlogPost reading time calculation."""
        blog_post = BlogPost(
            title="Test Post",
            description="Test description",
            content="# Test Post\n\n" + "word " * 300,  # 300 words
            category="development",
            tags=["test", "blog"]
        )
        
        # Should calculate reading time based on word count
        assert blog_post.reading_time > 0
        assert isinstance(blog_post.reading_time, int) 