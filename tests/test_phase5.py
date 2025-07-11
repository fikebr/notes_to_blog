"""
Tests for Phase 5: Workflow Orchestration.

Tests the blog post crew, input processor, output generator, and complete workflow.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import shutil

from src.crews.blog_post_crew import BlogPostCrew, WorkflowStep
from src.services.input_processor import InputProcessor
from src.services.output_generator import OutputGenerator
from src.models.config_models import Config
from src.models.blog_models import BlogPost, Note, FrontMatter, Image
from src.services import ServiceRegistry


class TestWorkflowStep:
    """Test WorkflowStep model."""
    
    def test_workflow_step_creation(self):
        """Test creating a workflow step."""
        step = WorkflowStep(
            step_number=1,
            name="Test Step",
            description="Test description"
        )
        
        assert step.step_number == 1
        assert step.name == "Test Step"
        assert step.description == "Test description"
        assert step.status == "pending"
        assert step.start_time is None
        assert step.end_time is None


class TestBlogPostCrew:
    """Test BlogPostCrew functionality."""
    
    @pytest.fixture
    def mock_config(self):
        """Create mock configuration."""
        config = Mock(spec=Config)
        config.paths.inbox_dir = "inbox"
        config.paths.output_dir = "output"
        config.paths.images_dir = "images"
        config.crewai.agent_verbose = True
        config.crewai.agent_max_iterations = 3
        config.crewai.agent_memory = True
        return config
    
    @pytest.fixture
    def mock_service_registry(self):
        """Create mock service registry."""
        registry = Mock(spec=ServiceRegistry)
        
        # Mock OpenRouter service
        openrouter_service = Mock()
        openrouter_service.create_crewai_adapter.return_value = Mock()
        registry.get_openrouter.return_value = openrouter_service
        
        # Mock Replicate service
        replicate_service = Mock()
        replicate_service.generate_image.return_value = "/path/to/image.jpg"
        registry.get_replicate.return_value = replicate_service
        
        return registry
    
    @pytest.fixture
    def blog_post_crew(self, mock_config, mock_service_registry):
        """Create blog post crew with mocked dependencies."""
        with patch('src.crews.blog_post_crew.ContentAnalyzerAgent'), \
             patch('src.crews.blog_post_crew.ResearchAgent'), \
             patch('src.crews.blog_post_crew.ContentWriterAgent'), \
             patch('src.crews.blog_post_crew.ImageGeneratorAgent'), \
             patch('src.crews.blog_post_crew.MetadataGeneratorAgent'):
            
            crew = BlogPostCrew(mock_config, mock_service_registry)
            
            # Mock agent methods
            crew.content_analyzer.analyze_notes.return_value = {
                "title": "Test Blog Post",
                "description": "Test description",
                "subheadings": ["Introduction", "Main Content", "Conclusion"]
            }
            
            crew.researcher.research_topic.return_value = {
                "summary": "Test research summary",
                "key_points": ["Point 1", "Point 2"],
                "sources": ["http://example.com"]
            }
            
            crew.researcher.research_subheading.return_value = {
                "summary": "Subheading research",
                "key_points": ["Sub point 1"],
                "sources": ["http://example2.com"]
            }
            
            crew.content_writer.write_introduction.return_value = "Test introduction"
            crew.content_writer.write_conclusion.return_value = "Test conclusion"
            crew.content_writer.expand_subheading.return_value = "Expanded content"
            
            crew.image_generator.create_image_prompts.return_value = {
                "header_image": "Header prompt",
                "supplemental_images": ["Prompt 1", "Prompt 2"]
            }
            
            crew.image_generator.generate_images.return_value = {
                "header": "/path/to/header.jpg",
                "supplemental_1": "/path/to/supp1.jpg"
            }
            
            crew.metadata_generator.generate_metadata.return_value = {
                "category": "development",
                "tags": ["programming", "blog"],
                "filename": "test-blog-post.md",
                "frontmatter": {
                    "title": "Test Blog Post",
                    "description": "Test description",
                    "date": "2025-01-27",
                    "draft": True,
                    "taxonomies": {
                        "categories": ["development"],
                        "tags": ["programming", "blog"]
                    }
                }
            }
            
            return crew
    
    def test_crew_initialization(self, blog_post_crew):
        """Test crew initialization."""
        assert blog_post_crew.config is not None
        assert blog_post_crew.service_registry is not None
        assert len(blog_post_crew.workflow_steps) == 15
        assert blog_post_crew.workflow_steps[0].step_number == 1
        assert blog_post_crew.workflow_steps[0].name == "Input Validation"
    
    def test_workflow_step_status_update(self, blog_post_crew):
        """Test updating workflow step status."""
        blog_post_crew._update_step_status(1, "in_progress")
        
        step = next(s for s in blog_post_crew.workflow_steps if s.step_number == 1)
        assert step.status == "in_progress"
        assert step.start_time is not None
    
    def test_workflow_status(self, blog_post_crew):
        """Test getting workflow status."""
        status = blog_post_crew.get_workflow_status()
        
        assert len(status) == 15
        assert all("step_number" in step for step in status)
        assert all("name" in step for step in status)
        assert all("status" in step for step in status)
    
    def test_health_check(self, blog_post_crew):
        """Test crew health check."""
        health = blog_post_crew.health_check()
        
        assert health["crew_name"] == "Blog Post Crew"
        assert health["status"] == "healthy"
        assert "agents" in health
        assert health["workflow_steps"] == 15
    
    def test_input_validation(self, blog_post_crew):
        """Test input validation step."""
        notes_content = "Test notes content"
        filename = "test_notes.txt"
        
        note = blog_post_crew._validate_input(notes_content, filename)
        
        assert note.content == notes_content
        assert note.filename == filename
        assert note.source == "inbox"
    
    def test_coordinate_research(self, blog_post_crew):
        """Test research coordination."""
        title = "Test Title"
        subheadings = ["Intro", "Main", "Conclusion"]
        
        research_data = blog_post_crew._coordinate_research(title, subheadings)
        
        assert "main_topic" in research_data
        assert len(research_data) == 4  # main_topic + 3 subheadings
        assert all(subheading in research_data for subheading in subheadings)
    
    def test_research_content(self, blog_post_crew):
        """Test content research expansion."""
        subheadings = ["Intro", "Main"]
        research_data = {
            "main_topic": {"summary": "Main research", "key_points": [], "sources": []},
            "Intro": {"summary": "Intro research", "key_points": [], "sources": []},
            "Main": {"summary": "Main research", "key_points": [], "sources": []}
        }
        
        expanded = blog_post_crew._research_content(subheadings, research_data)
        
        assert len(expanded) == 2
        assert "Intro" in expanded
        assert "Main" in expanded
        assert "combined_summary" in expanded["Intro"]
    
    def test_validate_sources(self, blog_post_crew):
        """Test source validation."""
        research_data = {
            "Intro": {
                "sources": ["http://example1.com", "http://example2.com"]
            }
        }
        
        validated = blog_post_crew._validate_sources(research_data)
        
        assert "Intro" in validated
        assert "validated_sources" in validated["Intro"]
        assert "citations" in validated["Intro"]
    
    def test_expand_content(self, blog_post_crew):
        """Test content expansion."""
        subheadings = ["Intro", "Main"]
        research_data = {
            "Intro": {"summary": "Test", "key_points": [], "sources": []},
            "Main": {"summary": "Test", "key_points": [], "sources": []}
        }
        
        expanded = blog_post_crew._expand_content(subheadings, research_data)
        
        assert len(expanded) == 2
        assert "Intro" in expanded
        assert "Main" in expanded
        assert expanded["Intro"] == "Expanded content"
    
    def test_generate_final_output(self, blog_post_crew):
        """Test final output generation."""
        title = "Test Title"
        description = "Test description"
        introduction = "Test introduction"
        expanded_content = {"Intro": "Content 1", "Main": "Content 2"}
        conclusion = "Test conclusion"
        generated_images = {"header": "/path/to/header.jpg"}
        metadata = {
            "category": "development",
            "tags": ["programming"],
            "filename": "test-post.md"
        }
        
        blog_post = blog_post_crew._generate_final_output(
            title, description, introduction, expanded_content,
            conclusion, generated_images, metadata
        )
        
        assert isinstance(blog_post, BlogPost)
        assert blog_post.frontmatter.title == title
        assert blog_post.frontmatter.description == description
        assert "Test introduction" in blog_post.content
        assert "Test conclusion" in blog_post.content
        assert len(blog_post.images) == 1


class TestInputProcessor:
    """Test InputProcessor functionality."""
    
    @pytest.fixture
    def mock_config(self):
        """Create mock configuration."""
        config = Mock(spec=Config)
        config.paths.inbox_dir = "inbox"
        return config
    
    @pytest.fixture
    def temp_inbox(self):
        """Create temporary inbox directory."""
        temp_dir = tempfile.mkdtemp()
        inbox_dir = Path(temp_dir) / "inbox"
        inbox_dir.mkdir()
        yield inbox_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def input_processor(self, mock_config, temp_inbox):
        """Create input processor with temporary inbox."""
        mock_config.paths.inbox_dir = str(temp_inbox)
        return InputProcessor(mock_config)
    
    def test_processor_initialization(self, input_processor):
        """Test input processor initialization."""
        assert input_processor.config is not None
        assert input_processor.inbox_path.exists()
    
    def test_supported_file_check(self, input_processor):
        """Test supported file checking."""
        # Test supported files
        assert input_processor._is_supported_file(Path("test.txt"))
        assert input_processor._is_supported_file(Path("test.md"))
        assert input_processor._is_supported_file(Path("test.markdown"))
        
        # Test unsupported files
        assert not input_processor._is_supported_file(Path("test.pdf"))
        assert not input_processor._is_supported_file(Path("test.exe"))
        assert not input_processor._is_supported_file(Path(".hidden.txt"))
    
    def test_file_validation(self, input_processor, temp_inbox):
        """Test file validation."""
        # Create a test file
        test_file = temp_inbox / "test.txt"
        test_file.write_text("Test content", encoding='utf-8')
        
        validation = input_processor.validate_note_file(test_file)
        
        assert validation["is_valid"] is True
        assert validation["file_path"] == str(test_file)
        assert validation["file_size"] > 0
        assert validation["file_type"] == ".txt"
        assert validation["encoding"] == "utf-8"
        assert validation["errors"] == []
    
    def test_file_validation_empty_file(self, input_processor, temp_inbox):
        """Test validation of empty file."""
        test_file = temp_inbox / "empty.txt"
        test_file.write_text("", encoding='utf-8')
        
        validation = input_processor.validate_note_file(test_file)
        
        assert validation["is_valid"] is False
        assert "File is empty" in validation["errors"]
    
    def test_file_validation_unsupported_extension(self, input_processor, temp_inbox):
        """Test validation of unsupported file extension."""
        test_file = temp_inbox / "test.pdf"
        test_file.write_text("Test content", encoding='utf-8')
        
        validation = input_processor.validate_note_file(test_file)
        
        assert validation["is_valid"] is False
        assert "Unsupported file extension" in validation["errors"][0]
    
    def test_process_file(self, input_processor, temp_inbox):
        """Test file processing."""
        test_file = temp_inbox / "test.txt"
        test_file.write_text("Test notes content", encoding='utf-8')
        
        note = input_processor._process_file(test_file)
        
        assert note is not None
        assert note.content == "Test notes content"
        assert note.filename == "test.txt"
        assert note.source == "inbox"
        assert note.file_path == str(test_file)
    
    def test_read_file_content(self, input_processor, temp_inbox):
        """Test file content reading."""
        test_file = temp_inbox / "test.txt"
        test_file.write_text("Test content with BOM\ufeff", encoding='utf-8-sig')
        
        content = input_processor._read_file_content(test_file, "utf-8-sig")
        
        assert content == "Test content with BOM"
    
    def test_read_file_content_whitespace_only(self, input_processor, temp_inbox):
        """Test reading whitespace-only file."""
        test_file = temp_inbox / "whitespace.txt"
        test_file.write_text("   \n\t   \n", encoding='utf-8')
        
        content = input_processor._read_file_content(test_file, "utf-8")
        
        assert content is None
    
    def test_get_inbox_status(self, input_processor, temp_inbox):
        """Test inbox status reporting."""
        # Create test files
        (temp_inbox / "test1.txt").write_text("Content 1")
        (temp_inbox / "test2.md").write_text("Content 2")
        (temp_inbox / "test3.pdf").write_text("Unsupported")
        
        status = input_processor.get_inbox_status()
        
        assert status["inbox_path"] == str(temp_inbox)
        assert status["total_files"] == 3
        assert status["supported_files"] == 2
        assert "supported_extensions" in status


class TestOutputGenerator:
    """Test OutputGenerator functionality."""
    
    @pytest.fixture
    def mock_config(self):
        """Create mock configuration."""
        config = Mock(spec=Config)
        config.paths.output_dir = "output"
        config.paths.images_dir = "images"
        return config
    
    @pytest.fixture
    def temp_output(self):
        """Create temporary output directory."""
        temp_dir = tempfile.mkdtemp()
        output_dir = Path(temp_dir) / "output"
        output_dir.mkdir()
        images_dir = Path(temp_dir) / "images"
        images_dir.mkdir()
        yield output_dir, images_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def output_generator(self, mock_config, temp_output):
        """Create output generator with temporary directories."""
        output_dir, images_dir = temp_output
        mock_config.paths.output_dir = str(output_dir)
        mock_config.paths.images_dir = str(images_dir)
        return OutputGenerator(mock_config)
    
    @pytest.fixture
    def sample_blog_post(self):
        """Create a sample blog post for testing."""
        frontmatter = FrontMatter(
            title="Test Blog Post",
            description="Test description",
            date="2025-01-27",
            draft=True,
            categories=["development"],
            tags=["programming", "blog"]
        )
        
        return BlogPost(
            frontmatter=frontmatter,
            content="# Test Content\n\nThis is test content for the blog post.",
            filename="test-blog-post.md",
            created_at=None,
            images=[]
        )
    
    def test_generator_initialization(self, output_generator):
        """Test output generator initialization."""
        assert output_generator.config is not None
        assert output_generator.output_path.exists()
        assert output_generator.images_path.exists()
    
    def test_blog_post_validation(self, output_generator, sample_blog_post):
        """Test blog post validation."""
        validation = output_generator._validate_blog_post(sample_blog_post)
        
        assert validation["is_valid"] is True
        assert validation["errors"] == []
    
    def test_blog_post_validation_missing_title(self, output_generator, sample_blog_post):
        """Test validation with missing title."""
        sample_blog_post.frontmatter.title = ""
        
        validation = output_generator._validate_blog_post(sample_blog_post)
        
        assert validation["is_valid"] is False
        assert "Missing title" in validation["errors"][0]
    
    def test_blog_post_validation_short_content(self, output_generator, sample_blog_post):
        """Test validation with short content."""
        sample_blog_post.content = "Short"
        
        validation = output_generator._validate_blog_post(sample_blog_post)
        
        assert validation["is_valid"] is False
        assert "Content too short" in validation["errors"][0]
    
    def test_frontmatter_generation(self, output_generator, sample_blog_post):
        """Test frontmatter content generation."""
        frontmatter_content = output_generator._generate_frontmatter_content(
            sample_blog_post.frontmatter
        )
        
        assert "+++" in frontmatter_content
        assert 'title = "Test Blog Post"' in frontmatter_content
        assert 'description = "Test description"' in frontmatter_content
        assert 'date = "2025-01-27"' in frontmatter_content
        assert 'draft = true' in frontmatter_content
        assert 'categories = ["development"]' in frontmatter_content
        assert 'tags = ["programming", "blog"]' in frontmatter_content
    
    def test_toml_string_escaping(self, output_generator):
        """Test TOML string escaping."""
        escaped = output_generator._escape_toml_string('Test "quoted" string with \\ backslash')
        
        assert '\\"' in escaped
        assert '\\\\' in escaped
    
    def test_toml_array_formatting(self, output_generator):
        """Test TOML array formatting."""
        formatted = output_generator._format_toml_array(["tag1", "tag2"])
        
        assert formatted == '["tag1", "tag2"]'
    
    def test_toml_array_formatting_empty(self, output_generator):
        """Test TOML array formatting with empty list."""
        formatted = output_generator._format_toml_array([])
        
        assert formatted == "[]"
    
    def test_output_file_path_generation(self, output_generator, temp_output):
        """Test output file path generation."""
        output_dir, _ = temp_output
        
        # Test basic path generation
        path = output_generator._get_output_file_path("test-post.md")
        assert path == output_dir / "test-post.md"
        
        # Test adding .md extension
        path = output_generator._get_output_file_path("test-post")
        assert path == output_dir / "test-post.md"
        
        # Test filename conflict resolution
        (output_dir / "test-post.md").write_text("Existing content")
        path = output_generator._get_output_file_path("test-post.md")
        assert path == output_dir / "test-post_1.md"
    
    def test_generate_blog_post_file(self, output_generator, sample_blog_post, temp_output):
        """Test complete blog post file generation."""
        output_dir, _ = temp_output
        
        result = output_generator.generate_blog_post_file(sample_blog_post)
        
        assert result["success"] is True
        assert result["file_path"] is not None
        assert result["file_size"] > 0
        assert result["content_length"] > 0
        
        # Check that file was actually created
        file_path = Path(result["file_path"])
        assert file_path.exists()
        
        # Check file content
        content = file_path.read_text(encoding='utf-8')
        assert "+++" in content
        assert "Test Blog Post" in content
        assert "# Test Content" in content
    
    def test_image_management(self, output_generator, temp_output):
        """Test image management."""
        output_dir, images_dir = temp_output
        
        # Create a test image
        test_image_path = Path(tempfile.mktemp(suffix='.jpg'))
        test_image_path.write_text("fake image content")
        
        images = [Image(path=str(test_image_path), alt_text="Test image")]
        blog_post_path = output_dir / "test-post.md"
        
        try:
            result = output_generator._manage_images(images, blog_post_path)
            
            assert len(result["copied"]) == 1
            assert len(result["failed"]) == 0
            assert len(result["not_found"]) == 0
            
            # Check that image was copied
            blog_post_images_dir = images_dir / "test-post"
            assert blog_post_images_dir.exists()
            
        finally:
            test_image_path.unlink(missing_ok=True)
    
    def test_output_file_validation(self, output_generator, temp_output):
        """Test output file validation."""
        output_dir, _ = temp_output
        
        # Create a valid test file
        test_file = output_dir / "test.md"
        test_file.write_text("""+++
title = "Test"
description = "Test description"
date = "2025-01-27"
draft = true

[taxonomies]
categories = ["development"]
tags = ["blog"]
+++

# Test Content

This is test content for validation.
""")
        
        validation = output_generator.validate_output_file(test_file)
        
        assert validation["is_valid"] is True
        assert validation["has_frontmatter"] is True
        assert validation["has_content"] is True
        assert validation["file_size"] > 0
        assert validation["errors"] == []
    
    def test_output_file_validation_missing_frontmatter(self, output_generator, temp_output):
        """Test validation of file without frontmatter."""
        output_dir, _ = temp_output
        
        test_file = output_dir / "test.md"
        test_file.write_text("# Test Content\n\nNo frontmatter here.")
        
        validation = output_generator.validate_output_file(test_file)
        
        assert validation["is_valid"] is False
        assert "Missing frontmatter" in validation["errors"][0]
    
    def test_get_output_status(self, output_generator, temp_output):
        """Test output status reporting."""
        output_dir, _ = temp_output
        
        # Create test files
        (output_dir / "valid1.md").write_text("+++\ntitle = 'Test'\ndescription = 'Test'\n+++\n\nContent")
        (output_dir / "valid2.md").write_text("+++\ntitle = 'Test2'\ndescription = 'Test2'\n+++\n\nContent2")
        (output_dir / "invalid.md").write_text("No frontmatter")
        
        status = output_generator.get_output_status()
        
        assert status["output_path"] == str(output_dir)
        assert status["total_files"] == 3
        assert status["valid_files"] == 2
        assert status["invalid_files"] == 1
        assert status["total_size_bytes"] > 0


if __name__ == "__main__":
    pytest.main([__file__]) 