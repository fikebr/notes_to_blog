"""
Unit tests for services.
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path

from src.services.openrouter_service import OpenRouterService
from src.services.replicate_service import ReplicateService
from src.services.brave_search_service import BraveSearchService
from src.services.template_service import TemplateService
from src.services.file_structure_service import FileStructureService
from src.services.input_processor import InputProcessor
from src.services.output_generator import OutputGenerator
from src.services.service_registry import ServiceRegistry


class TestOpenRouterService:
    """Test OpenRouter service."""
    
    def test_init_valid_config(self, test_config):
        """Test service initialization with valid config."""
        service = OpenRouterService(test_config.api)
        assert service.config == test_config.api
        assert service.client is not None

    def test_generate_text_sync(self, test_config, mock_openrouter_service):
        """Test synchronous text generation."""
        service = OpenRouterService(test_config.api)
        result = service.generate_text("Test prompt")
        assert result == "Mock generated text"

    @pytest.mark.asyncio
    async def test_generate_text_async(self, test_config, mock_openrouter_service):
        """Test asynchronous text generation."""
        service = OpenRouterService(test_config.api)
        result = await service.generate_text_async("Test prompt")
        assert result == "Mock async generated text"

    def test_generate_text_with_parameters(self, test_config, mock_openrouter_service):
        """Test text generation with custom parameters."""
        service = OpenRouterService(test_config.api)
        result = service.generate_text(
            "Test prompt",
            max_tokens=1000,
            temperature=0.5
        )
        assert result == "Mock generated text"

    def test_handle_api_error(self, test_config):
        """Test API error handling."""
        service = OpenRouterService(test_config.api)
        with pytest.raises(Exception):
            service._handle_api_error("Test error", 500)

    def test_validate_prompt(self, test_config):
        """Test prompt validation."""
        service = OpenRouterService(test_config.api)
        
        # Valid prompt
        assert service._validate_prompt("Valid prompt") is True
        
        # Empty prompt
        with pytest.raises(ValueError):
            service._validate_prompt("")

        # Too long prompt
        long_prompt = "x" * 100000
        with pytest.raises(ValueError):
            service._validate_prompt(long_prompt)


class TestReplicateService:
    """Test Replicate service."""
    
    def test_init_valid_config(self, test_config):
        """Test service initialization with valid config."""
        service = ReplicateService(test_config.api)
        assert service.config == test_config.api
        assert service.client is not None

    def test_generate_image_sync(self, test_config, mock_replicate_service):
        """Test synchronous image generation."""
        service = ReplicateService(test_config.api)
        result = service.generate_image("Test prompt")
        assert result["id"] == "test-image-id"
        assert result["url"] == "https://example.com/test-image.jpg"

    @pytest.mark.asyncio
    async def test_generate_image_async(self, test_config, mock_replicate_service):
        """Test asynchronous image generation."""
        service = ReplicateService(test_config.api)
        result = await service.generate_image_async("Test prompt")
        assert result["id"] == "test-image-id"
        assert result["url"] == "https://example.com/test-image.jpg"

    def test_generate_image_with_parameters(self, test_config, mock_replicate_service):
        """Test image generation with custom parameters."""
        service = ReplicateService(test_config.api)
        result = service.generate_image(
            "Test prompt",
            width=512,
            height=512,
            guidance_scale=8.0
        )
        assert result["id"] == "test-image-id"

    def test_validate_image_prompt(self, test_config):
        """Test image prompt validation."""
        service = ReplicateService(test_config.api)
        
        # Valid prompt
        assert service._validate_image_prompt("Valid prompt") is True
        
        # Empty prompt
        with pytest.raises(ValueError):
            service._validate_image_prompt("")

        # Too long prompt
        long_prompt = "x" * 1000
        with pytest.raises(ValueError):
            service._validate_image_prompt(long_prompt)

    def test_validate_dimensions(self, test_config):
        """Test image dimension validation."""
        service = ReplicateService(test_config.api)
        
        # Valid dimensions
        assert service._validate_dimensions(512, 512) is True
        assert service._validate_dimensions(1024, 1024) is True
        
        # Invalid dimensions
        with pytest.raises(ValueError):
            service._validate_dimensions(100, 512)  # Too small
        
        with pytest.raises(ValueError):
            service._validate_dimensions(2048, 2048)  # Too large


class TestBraveSearchService:
    """Test Brave Search service."""
    
    def test_init_valid_config(self, test_config):
        """Test service initialization with valid config."""
        service = BraveSearchService(test_config.api)
        assert service.config == test_config.api
        assert service.client is not None

    def test_search_sync(self, test_config, mock_brave_search_service):
        """Test synchronous search."""
        service = BraveSearchService(test_config.api)
        result = service.search("test query")
        assert result["query"] == "test query"
        assert len(result["results"]) == 2

    @pytest.mark.asyncio
    async def test_search_async(self, test_config, mock_brave_search_service):
        """Test asynchronous search."""
        service = BraveSearchService(test_config.api)
        result = await service.search_async("test query")
        assert result["query"] == "test query"
        assert len(result["results"]) == 2

    def test_search_with_parameters(self, test_config, mock_brave_search_service):
        """Test search with custom parameters."""
        service = BraveSearchService(test_config.api)
        result = service.search(
            "test query",
            max_results=5,
            search_lang="en"
        )
        assert result["query"] == "test query"

    def test_validate_query(self, test_config):
        """Test query validation."""
        service = BraveSearchService(test_config.api)
        
        # Valid query
        assert service._validate_query("Valid query") is True
        
        # Empty query
        with pytest.raises(ValueError):
            service._validate_query("")

        # Too long query
        long_query = "x" * 1000
        with pytest.raises(ValueError):
            service._validate_query(long_query)

    def test_filter_results(self, test_config):
        """Test result filtering."""
        service = BraveSearchService(test_config.api)
        
        results = [
            {"title": "Result 1", "url": "https://example.com/1", "description": "Desc 1"},
            {"title": "Result 2", "url": "https://example.com/2", "description": "Desc 2"},
            {"title": "Result 3", "url": "https://example.com/3", "description": "Desc 3"}
        ]
        
        filtered = service._filter_results(results, max_results=2)
        assert len(filtered) == 2


class TestTemplateService:
    """Test Template service."""
    
    def test_init(self):
        """Test service initialization."""
        service = TemplateService()
        assert service.template_dir == Path("templates")

    def test_load_template_success(self):
        """Test successful template loading."""
        service = TemplateService()
        template = service.load_template("frontmatter_template.md")
        assert template is not None
        assert "+++" in template

    def test_load_template_not_found(self):
        """Test template loading when file not found."""
        service = TemplateService()
        with pytest.raises(FileNotFoundError):
            service.load_template("nonexistent_template.md")

    def test_render_template(self):
        """Test template rendering."""
        service = TemplateService()
        template = "Hello {{ name }}!"
        context = {"name": "World"}
        result = service.render_template(template, context)
        assert result == "Hello World!"

    def test_render_template_with_filters(self):
        """Test template rendering with filters."""
        service = TemplateService()
        template = "Title: {{ title | title }}"
        context = {"title": "hello world"}
        result = service.render_template(template, context)
        assert result == "Title: Hello World"

    def test_validate_template(self):
        """Test template validation."""
        service = TemplateService()
        
        # Valid template
        assert service.validate_template("Valid template") is True
        
        # Empty template
        with pytest.raises(ValueError):
            service.validate_template("")

    def test_get_template_path(self):
        """Test template path resolution."""
        service = TemplateService()
        path = service.get_template_path("test.md")
        assert path == Path("templates/test.md")


class TestFileStructureService:
    """Test File Structure service."""
    
    def test_init(self):
        """Test service initialization."""
        service = FileStructureService()
        assert service.inbox_dir == Path("inbox")
        assert service.output_dir == Path("output")
        assert service.images_dir == Path("images")

    def test_create_directories(self, temp_dir):
        """Test directory creation."""
        service = FileStructureService()
        service.inbox_dir = temp_dir / "inbox"
        service.output_dir = temp_dir / "output"
        service.images_dir = temp_dir / "images"
        
        service.create_directories()
        
        assert service.inbox_dir.exists()
        assert service.output_dir.exists()
        assert service.images_dir.exists()

    def test_validate_directory(self, temp_dir):
        """Test directory validation."""
        service = FileStructureService()
        
        # Valid directory
        valid_dir = temp_dir / "valid"
        valid_dir.mkdir()
        assert service.validate_directory(valid_dir) is True
        
        # Non-existent directory
        with pytest.raises(ValueError):
            service.validate_directory(temp_dir / "nonexistent")

    def test_get_directory_info(self, temp_dir):
        """Test directory info retrieval."""
        service = FileStructureService()
        
        # Create test directory with files
        test_dir = temp_dir / "test"
        test_dir.mkdir()
        (test_dir / "file1.txt").write_text("content1")
        (test_dir / "file2.txt").write_text("content2")
        
        info = service.get_directory_info(test_dir)
        assert info["path"] == str(test_dir)
        assert info["file_count"] == 2
        assert info["exists"] is True

    def test_list_directory_contents(self, temp_dir):
        """Test directory content listing."""
        service = FileStructureService()
        
        # Create test directory with files
        test_dir = temp_dir / "test"
        test_dir.mkdir()
        (test_dir / "file1.txt").write_text("content1")
        (test_dir / "subdir").mkdir()
        (test_dir / "subdir" / "file2.txt").write_text("content2")
        
        contents = service.list_directory_contents(test_dir)
        assert len(contents["files"]) == 1
        assert len(contents["directories"]) == 1

    def test_get_storage_usage(self, temp_dir):
        """Test storage usage calculation."""
        service = FileStructureService()
        
        # Create test directory with files
        test_dir = temp_dir / "test"
        test_dir.mkdir()
        (test_dir / "file1.txt").write_text("content1")
        (test_dir / "file2.txt").write_text("content2")
        
        usage = service.get_storage_usage(test_dir)
        assert usage["total_size"] > 0
        assert usage["file_count"] == 2

    def test_cleanup_directory(self, temp_dir):
        """Test directory cleanup."""
        service = FileStructureService()
        
        # Create test directory with files
        test_dir = temp_dir / "test"
        test_dir.mkdir()
        (test_dir / "file1.txt").write_text("content1")
        (test_dir / "file2.txt").write_text("content2")
        
        service.cleanup_directory(test_dir, max_age_days=0)
        
        # Files should be removed
        assert not (test_dir / "file1.txt").exists()
        assert not (test_dir / "file2.txt").exists()


class TestInputProcessor:
    """Test Input Processor service."""
    
    def test_init(self):
        """Test service initialization."""
        processor = InputProcessor()
        assert processor.inbox_dir == Path("inbox")

    def test_scan_inbox(self, temp_dir):
        """Test inbox scanning."""
        processor = InputProcessor()
        processor.inbox_dir = temp_dir / "inbox"
        processor.inbox_dir.mkdir()
        
        # Create test files
        (processor.inbox_dir / "note1.md").write_text("# Test Note 1")
        (processor.inbox_dir / "note2.txt").write_text("Test Note 2")
        (processor.inbox_dir / "ignore.pdf").write_text("PDF content")
        
        files = processor.scan_inbox()
        assert len(files) == 2  # Only markdown and text files
        assert "note1.md" in [f.name for f in files]
        assert "note2.txt" in [f.name for f in files]

    def test_parse_note_markdown(self, temp_dir):
        """Test markdown note parsing."""
        processor = InputProcessor()
        
        content = "# Test Note\n\nThis is test content.\n\n## Section\n\nMore content."
        note = processor.parse_note(content, "test.md", "markdown")
        
        assert note.content == content
        assert note.source_file == "test.md"
        assert note.file_type == "markdown"

    def test_parse_note_text(self, temp_dir):
        """Test text note parsing."""
        processor = InputProcessor()
        
        content = "This is plain text content."
        note = processor.parse_note(content, "test.txt", "text")
        
        assert note.content == content
        assert note.source_file == "test.txt"
        assert note.file_type == "text"

    def test_validate_note(self):
        """Test note validation."""
        processor = InputProcessor()
        
        # Valid note
        note = processor.parse_note("Valid content", "test.md", "markdown")
        assert processor.validate_note(note) is True
        
        # Invalid note (empty content)
        with pytest.raises(ValueError):
            processor.parse_note("", "test.md", "markdown")

    def test_get_supported_formats(self):
        """Test supported format detection."""
        processor = InputProcessor()
        formats = processor.get_supported_formats()
        assert "markdown" in formats
        assert "text" in formats


class TestOutputGenerator:
    """Test Output Generator service."""
    
    def test_init(self):
        """Test service initialization."""
        generator = OutputGenerator()
        assert generator.output_dir == Path("output")
        assert generator.images_dir == Path("images")

    def test_generate_markdown_file(self, temp_dir, sample_blog_post_data):
        """Test markdown file generation."""
        generator = OutputGenerator()
        generator.output_dir = temp_dir / "output"
        generator.output_dir.mkdir()
        
        from src.models.blog_models import BlogPost, Image
        
        blog_post = BlogPost(**sample_blog_post_data)
        
        file_path = generator.generate_markdown_file(blog_post)
        assert file_path.exists()
        assert file_path.suffix == ".md"
        
        content = file_path.read_text()
        assert "+++" in content
        assert "Test Blog Post" in content

    def test_insert_frontmatter(self, sample_frontmatter):
        """Test frontmatter insertion."""
        generator = OutputGenerator()
        
        content = "# Test Post\n\nContent here."
        result = generator.insert_frontmatter(content, sample_frontmatter)
        
        assert "+++" in result
        assert "title = \"Test Blog Post\"" in result
        assert "# Test Post" in result

    def test_save_image(self, temp_dir):
        """Test image saving."""
        generator = OutputGenerator()
        generator.images_dir = temp_dir / "images"
        generator.images_dir.mkdir()
        
        from src.models.blog_models import Image
        
        image = Image(
            url="https://example.com/image.jpg",
            alt_text="Test image",
            caption="A test image"
        )
        
        # Mock image download
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = Mock()
            mock_response.read.return_value = b"fake image data"
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = generator.save_image(image)
            assert result is not None

    def test_validate_output(self, temp_dir):
        """Test output validation."""
        generator = OutputGenerator()
        
        # Create test output file
        test_file = temp_dir / "test.md"
        test_file.write_text("# Test Post\n\nContent here.")
        
        assert generator.validate_output(test_file) is True
        
        # Test with non-existent file
        with pytest.raises(ValueError):
            generator.validate_output(temp_dir / "nonexistent.md")

    def test_generate_filename(self):
        """Test filename generation."""
        generator = OutputGenerator()
        
        filename = generator.generate_filename("Test Blog Post Title")
        assert filename.startswith("test-blog-post-title")
        assert filename.endswith(".md")

    def test_cleanup_old_files(self, temp_dir):
        """Test old file cleanup."""
        generator = OutputGenerator()
        generator.output_dir = temp_dir / "output"
        generator.output_dir.mkdir()
        
        # Create test files
        (generator.output_dir / "old_file.md").write_text("old content")
        (generator.output_dir / "new_file.md").write_text("new content")
        
        generator.cleanup_old_files(max_age_days=0)
        
        # Old files should be removed
        assert not (generator.output_dir / "old_file.md").exists()


class TestServiceRegistry:
    """Test Service Registry."""
    
    def test_init(self, test_config):
        """Test registry initialization."""
        registry = ServiceRegistry(test_config)
        assert registry.config == test_config
        assert registry.services == {}

    def test_register_service(self, test_config):
        """Test service registration."""
        registry = ServiceRegistry(test_config)
        
        mock_service = Mock()
        registry.register_service("test_service", mock_service)
        
        assert "test_service" in registry.services
        assert registry.services["test_service"] == mock_service

    def test_get_service(self, test_config):
        """Test service retrieval."""
        registry = ServiceRegistry(test_config)
        
        mock_service = Mock()
        registry.register_service("test_service", mock_service)
        
        retrieved = registry.get_service("test_service")
        assert retrieved == mock_service

    def test_get_service_not_found(self, test_config):
        """Test service retrieval when not found."""
        registry = ServiceRegistry(test_config)
        
        with pytest.raises(KeyError):
            registry.get_service("nonexistent_service")

    def test_health_check(self, test_config):
        """Test health check functionality."""
        registry = ServiceRegistry(test_config)
        
        # Mock healthy service
        healthy_service = Mock()
        healthy_service.health_check.return_value = {"status": "healthy"}
        registry.register_service("healthy_service", healthy_service)
        
        # Mock unhealthy service
        unhealthy_service = Mock()
        unhealthy_service.health_check.return_value = {"status": "unhealthy", "error": "Test error"}
        registry.register_service("unhealthy_service", unhealthy_service)
        
        health = registry.health_check()
        assert "healthy_service" in health
        assert "unhealthy_service" in health
        assert health["healthy_service"]["status"] == "healthy"
        assert health["unhealthy_service"]["status"] == "unhealthy"

    def test_list_services(self, test_config):
        """Test service listing."""
        registry = ServiceRegistry(test_config)
        
        registry.register_service("service1", Mock())
        registry.register_service("service2", Mock())
        
        services = registry.list_services()
        assert "service1" in services
        assert "service2" in services

    def test_remove_service(self, test_config):
        """Test service removal."""
        registry = ServiceRegistry(test_config)
        
        mock_service = Mock()
        registry.register_service("test_service", mock_service)
        
        registry.remove_service("test_service")
        assert "test_service" not in registry.services 