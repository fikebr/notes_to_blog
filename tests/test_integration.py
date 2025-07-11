"""
Integration tests for end-to-end workflow.
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path
import tempfile
import shutil

from src.crews.blog_post_crew import BlogPostCrew
from src.services.input_processor import InputProcessor
from src.services.output_generator import OutputGenerator
from src.services.service_registry import ServiceRegistry
from src.models.blog_models import Note, BlogPost


class TestEndToEndWorkflow:
    """Test complete end-to-end workflow."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        
        # Create directory structure
        (temp_dir / "inbox").mkdir()
        (temp_dir / "output").mkdir()
        (temp_dir / "images").mkdir()
        (temp_dir / "templates").mkdir()
        (temp_dir / "templates" / "agent_prompts").mkdir()
        (temp_dir / "templates" / "crew_prompts").mkdir()
        
        # Create sample note
        note_content = """
        # Python Programming Notes
        
        ## Key Concepts
        - Functions are reusable blocks of code
        - Classes provide object-oriented programming
        - Modules help organize code
        
        ## Best Practices
        - Use descriptive variable names
        - Write docstrings for functions
        - Follow PEP 8 style guidelines
        
        ## Examples
        Here are some examples of good Python code.
        """
        
        (temp_dir / "inbox" / "python_notes.md").write_text(note_content)
        
        yield temp_dir
        
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def mock_services(self, test_config):
        """Create mock services for testing."""
        with patch('src.services.openrouter_service.OpenRouterService') as mock_openrouter:
            with patch('src.services.replicate_service.ReplicateService') as mock_replicate:
                with patch('src.services.brave_search_service.BraveSearchService') as mock_brave:
                    
                    # Mock OpenRouter responses
                    mock_openrouter.return_value.generate_text.return_value = "Mock generated text"
                    mock_openrouter.return_value.generate_text_async.return_value = "Mock async text"
                    
                    # Mock Replicate responses
                    mock_replicate.return_value.generate_image.return_value = {
                        "id": "test-image-id",
                        "url": "https://example.com/test-image.jpg",
                        "status": "succeeded"
                    }
                    mock_replicate.return_value.generate_image_async.return_value = {
                        "id": "test-image-id",
                        "url": "https://example.com/test-image.jpg",
                        "status": "succeeded"
                    }
                    
                    # Mock Brave Search responses
                    mock_brave.return_value.search.return_value = {
                        "query": "test query",
                        "results": [
                            {
                                "title": "Test Result 1",
                                "url": "https://example.com/1",
                                "description": "Test description 1"
                            },
                            {
                                "title": "Test Result 2",
                                "url": "https://example.com/2",
                                "description": "Test description 2"
                            }
                        ]
                    }
                    mock_brave.return_value.search_async.return_value = {
                        "query": "test query",
                        "results": [
                            {
                                "title": "Test Result 1",
                                "url": "https://example.com/1",
                                "description": "Test description 1"
                            },
                            {
                                "title": "Test Result 2",
                                "url": "https://example.com/2",
                                "description": "Test description 2"
                            }
                        ]
                    }
                    
                    yield {
                        "openrouter": mock_openrouter.return_value,
                        "replicate": mock_replicate.return_value,
                        "brave": mock_brave.return_value
                    }

    def test_complete_workflow_sync(self, test_config, temp_workspace, mock_services):
        """Test complete synchronous workflow."""
        # Initialize services
        input_processor = InputProcessor()
        input_processor.inbox_dir = temp_workspace / "inbox"
        
        output_generator = OutputGenerator()
        output_generator.output_dir = temp_workspace / "output"
        output_generator.images_dir = temp_workspace / "images"
        
        # Scan inbox
        note_files = input_processor.scan_inbox()
        assert len(note_files) == 1
        assert note_files[0].name == "python_notes.md"
        
        # Parse note
        note_content = note_files[0].read_text()
        note = input_processor.parse_note(note_content, note_files[0].name, "markdown")
        assert note.content == note_content
        assert note.source_file == "python_notes.md"
        
        # Create blog post crew
        crew = BlogPostCrew(test_config)
        
        # Process note (with mocked services)
        with patch.object(crew, 'process_note') as mock_process:
            mock_process.return_value = BlogPost(
                title="Python Programming Guide",
                description="A comprehensive guide to Python programming concepts and best practices",
                content="# Python Programming Guide\n\nThis is a comprehensive guide...",
                category="development",
                tags=["python", "programming", "tutorial"],
                images=[]
            )
            
            blog_post = crew.process_note(note)
            
            assert blog_post.title == "Python Programming Guide"
            assert blog_post.category == "development"
            assert len(blog_post.tags) == 3
        
        # Generate output
        output_file = output_generator.generate_markdown_file(blog_post)
        assert output_file.exists()
        assert output_file.suffix == ".md"
        
        # Validate output
        content = output_file.read_text()
        assert "+++" in content
        assert "Python Programming Guide" in content
        assert "development" in content

    @pytest.mark.asyncio
    async def test_complete_workflow_async(self, test_config, temp_workspace, mock_services):
        """Test complete asynchronous workflow."""
        # Initialize services
        input_processor = InputProcessor()
        input_processor.inbox_dir = temp_workspace / "inbox"
        
        output_generator = OutputGenerator()
        output_generator.output_dir = temp_workspace / "output"
        output_generator.images_dir = temp_workspace / "images"
        
        # Scan inbox
        note_files = input_processor.scan_inbox()
        assert len(note_files) == 1
        
        # Parse note
        note_content = note_files[0].read_text()
        note = input_processor.parse_note(note_content, note_files[0].name, "markdown")
        
        # Create blog post crew
        crew = BlogPostCrew(test_config)
        
        # Process note asynchronously (with mocked services)
        with patch.object(crew, 'process_note_async') as mock_process:
            mock_process.return_value = BlogPost(
                title="Async Python Programming Guide",
                description="An asynchronous guide to Python programming",
                content="# Async Python Programming Guide\n\nThis is an async guide...",
                category="development",
                tags=["python", "async", "programming"],
                images=[]
            )
            
            blog_post = await crew.process_note_async(note)
            
            assert blog_post.title == "Async Python Programming Guide"
            assert blog_post.category == "development"
        
        # Generate output
        output_file = output_generator.generate_markdown_file(blog_post)
        assert output_file.exists()

    def test_workflow_with_images(self, test_config, temp_workspace, mock_services):
        """Test workflow with image generation."""
        # Initialize services
        input_processor = InputProcessor()
        input_processor.inbox_dir = temp_workspace / "inbox"
        
        output_generator = OutputGenerator()
        output_generator.output_dir = temp_workspace / "output"
        output_generator.images_dir = temp_workspace / "images"
        
        # Parse note
        note_files = input_processor.scan_inbox()
        note_content = note_files[0].read_text()
        note = input_processor.parse_note(note_content, note_files[0].name, "markdown")
        
        # Create blog post with images
        blog_post = BlogPost(
            title="Python Programming with Images",
            description="A guide with generated images",
            content="# Python Programming\n\nContent with images...",
            category="development",
            tags=["python", "images", "tutorial"],
            images=[
                {
                    "url": "https://example.com/image1.jpg",
                    "alt_text": "Python code example",
                    "caption": "Example Python code"
                }
            ]
        )
        
        # Generate output with images
        output_file = output_generator.generate_markdown_file(blog_post)
        assert output_file.exists()
        
        # Check that images directory exists
        assert output_generator.images_dir.exists()

    def test_workflow_error_handling(self, test_config, temp_workspace):
        """Test workflow error handling."""
        # Initialize services
        input_processor = InputProcessor()
        input_processor.inbox_dir = temp_workspace / "inbox"
        
        # Test with invalid note
        with pytest.raises(ValueError):
            input_processor.parse_note("", "empty.md", "markdown")
        
        # Test with non-existent file
        with pytest.raises(FileNotFoundError):
            input_processor.parse_note("content", "nonexistent.md", "markdown")

    def test_workflow_with_different_formats(self, test_config, temp_workspace):
        """Test workflow with different input formats."""
        # Initialize services
        input_processor = InputProcessor()
        input_processor.inbox_dir = temp_workspace / "inbox"
        
        # Create text file
        text_content = "This is a plain text note about Python programming."
        (temp_workspace / "inbox" / "text_note.txt").write_text(text_content)
        
        # Scan inbox
        note_files = input_processor.scan_inbox()
        assert len(note_files) == 2  # markdown + text
        
        # Parse text note
        text_note = input_processor.parse_note(text_content, "text_note.txt", "text")
        assert text_note.file_type == "text"
        assert text_note.content == text_content

    def test_workflow_batch_processing(self, test_config, temp_workspace, mock_services):
        """Test batch processing workflow."""
        # Create multiple notes
        notes = [
            ("note1.md", "# Note 1\n\nContent 1"),
            ("note2.md", "# Note 2\n\nContent 2"),
            ("note3.md", "# Note 3\n\nContent 3")
        ]
        
        for filename, content in notes:
            (temp_workspace / "inbox" / filename).write_text(content)
        
        # Initialize services
        input_processor = InputProcessor()
        input_processor.inbox_dir = temp_workspace / "inbox"
        
        output_generator = OutputGenerator()
        output_generator.output_dir = temp_workspace / "output"
        
        # Scan inbox
        note_files = input_processor.scan_inbox()
        assert len(note_files) == 4  # 3 new + 1 existing
        
        # Process all notes
        processed_notes = []
        for note_file in note_files:
            content = note_file.read_text()
            note = input_processor.parse_note(content, note_file.name, "markdown")
            processed_notes.append(note)
        
        assert len(processed_notes) == 4

    def test_workflow_performance(self, test_config, temp_workspace, mock_services):
        """Test workflow performance."""
        import time
        
        # Initialize services
        input_processor = InputProcessor()
        input_processor.inbox_dir = temp_workspace / "inbox"
        
        output_generator = OutputGenerator()
        output_generator.output_dir = temp_workspace / "output"
        
        # Measure processing time
        start_time = time.time()
        
        # Process note
        note_files = input_processor.scan_inbox()
        note_content = note_files[0].read_text()
        note = input_processor.parse_note(note_content, note_files[0].name, "markdown")
        
        # Create simple blog post
        blog_post = BlogPost(
            title="Performance Test",
            description="Testing performance",
            content="# Performance Test\n\nContent here.",
            category="development",
            tags=["test", "performance"]
        )
        
        # Generate output
        output_file = output_generator.generate_markdown_file(blog_post)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should complete within reasonable time (5 seconds)
        assert processing_time < 5.0
        assert output_file.exists()

    def test_workflow_data_persistence(self, test_config, temp_workspace):
        """Test data persistence in workflow."""
        # Initialize services
        input_processor = InputProcessor()
        input_processor.inbox_dir = temp_workspace / "inbox"
        
        output_generator = OutputGenerator()
        output_generator.output_dir = temp_workspace / "output"
        
        # Process note
        note_files = input_processor.scan_inbox()
        note_content = note_files[0].read_text()
        note = input_processor.parse_note(note_content, note_files[0].name, "markdown")
        
        # Create blog post
        blog_post = BlogPost(
            title="Persistence Test",
            description="Testing data persistence",
            content="# Persistence Test\n\nContent here.",
            category="development",
            tags=["test", "persistence"]
        )
        
        # Generate output
        output_file = output_generator.generate_markdown_file(blog_post)
        
        # Verify persistence
        assert output_file.exists()
        assert output_file.stat().st_size > 0
        
        # Read back and verify content
        content = output_file.read_text()
        assert "Persistence Test" in content
        assert "development" in content

    def test_workflow_concurrent_processing(self, test_config, temp_workspace, mock_services):
        """Test concurrent processing capabilities."""
        import threading
        import time
        
        # Create multiple notes
        for i in range(3):
            content = f"# Note {i}\n\nContent for note {i}"
            (temp_workspace / "inbox" / f"concurrent_note_{i}.md").write_text(content)
        
        # Initialize services
        input_processor = InputProcessor()
        input_processor.inbox_dir = temp_workspace / "inbox"
        
        output_generator = OutputGenerator()
        output_generator.output_dir = temp_workspace / "output"
        
        # Process notes concurrently
        results = []
        errors = []
        
        def process_note(note_file):
            try:
                content = note_file.read_text()
                note = input_processor.parse_note(content, note_file.name, "markdown")
                
                blog_post = BlogPost(
                    title=f"Concurrent {note_file.stem}",
                    description=f"Concurrent processing test {note_file.stem}",
                    content=f"# Concurrent {note_file.stem}\n\nContent here.",
                    category="development",
                    tags=["concurrent", "test"]
                )
                
                output_file = output_generator.generate_markdown_file(blog_post)
                results.append(output_file)
            except Exception as e:
                errors.append(e)
        
        # Start concurrent processing
        threads = []
        note_files = input_processor.scan_inbox()
        
        for note_file in note_files:
            thread = threading.Thread(target=process_note, args=(note_file,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify results
        assert len(errors) == 0
        assert len(results) == len(note_files)
        
        # Verify all output files exist
        for output_file in results:
            assert output_file.exists()


class TestServiceIntegration:
    """Test service integration."""
    
    def test_service_registry_integration(self, test_config):
        """Test service registry integration."""
        registry = ServiceRegistry(test_config)
        
        # Register services
        mock_openrouter = Mock()
        mock_replicate = Mock()
        mock_brave = Mock()
        
        registry.register_service("openrouter", mock_openrouter)
        registry.register_service("replicate", mock_replicate)
        registry.register_service("brave", mock_brave)
        
        # Verify services are registered
        assert registry.get_service("openrouter") == mock_openrouter
        assert registry.get_service("replicate") == mock_replicate
        assert registry.get_service("brave") == mock_brave
        
        # Test health check
        health = registry.health_check()
        assert "openrouter" in health
        assert "replicate" in health
        assert "brave" in health

    def test_agent_service_integration(self, test_config, mock_services):
        """Test agent and service integration."""
        from src.agents.content_analyzer import ContentAnalyzer
        from src.agents.researcher import Researcher
        
        # Create agents
        content_analyzer = ContentAnalyzer(test_config)
        researcher = Researcher(test_config)
        
        # Test agent initialization
        assert content_analyzer.config == test_config
        assert researcher.config == test_config
        
        # Test agent methods (with mocked services)
        note_content = "Test note content about Python programming"
        
        # These should not raise exceptions with mocked services
        assert content_analyzer.name == "content_analyzer"
        assert researcher.name == "researcher"

    def test_crew_agent_integration(self, test_config, mock_services):
        """Test crew and agent integration."""
        crew = BlogPostCrew(test_config)
        
        # Verify crew has all required agents
        assert hasattr(crew, 'content_analyzer')
        assert hasattr(crew, 'researcher')
        assert hasattr(crew, 'content_writer')
        assert hasattr(crew, 'image_generator')
        assert hasattr(crew, 'metadata_generator')
        
        # Verify crew configuration
        assert crew.config == test_config

    def test_template_service_integration(self):
        """Test template service integration."""
        from src.services.template_service import TemplateService
        
        template_service = TemplateService()
        
        # Test template loading
        template = template_service.load_template("frontmatter_template.md")
        assert template is not None
        assert "+++" in template
        
        # Test template rendering
        context = {
            "title": "Test Title",
            "description": "Test Description",
            "date": "2025-01-27",
            "draft": True,
            "category": "development",
            "tags": ["test", "blog"]
        }
        
        rendered = template_service.render_template(template, context)
        assert "Test Title" in rendered
        assert "development" in rendered

    def test_file_structure_service_integration(self, temp_workspace):
        """Test file structure service integration."""
        from src.services.file_structure_service import FileStructureService
        
        file_service = FileStructureService()
        file_service.inbox_dir = temp_workspace / "inbox"
        file_service.output_dir = temp_workspace / "output"
        file_service.images_dir = temp_workspace / "images"
        
        # Test directory validation
        assert file_service.validate_directory(temp_workspace / "inbox") is True
        assert file_service.validate_directory(temp_workspace / "output") is True
        assert file_service.validate_directory(temp_workspace / "images") is True
        
        # Test directory info
        info = file_service.get_directory_info(temp_workspace / "inbox")
        assert info["exists"] is True
        assert info["file_count"] >= 1
        
        # Test content listing
        contents = file_service.list_directory_contents(temp_workspace / "inbox")
        assert len(contents["files"]) >= 1 