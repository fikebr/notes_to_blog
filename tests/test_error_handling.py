"""
Error handling validation tests.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import shutil

from src.services.openrouter_service import OpenRouterService
from src.services.replicate_service import ReplicateService
from src.services.brave_search_service import BraveSearchService
from src.services.template_service import TemplateService
from src.services.file_structure_service import FileStructureService
from src.services.input_processor import InputProcessor
from src.services.output_generator import OutputGenerator
from src.agents.base_agent import BaseAgent
from src.agents.content_analyzer import ContentAnalyzer
from src.crews.blog_post_crew import BlogPostCrew
from src.models.blog_models import Note, BlogPost


class TestServiceErrorHandling:
    """Test error handling in services."""
    
    def test_openrouter_service_errors(self, test_config):
        """Test OpenRouter service error handling."""
        service = OpenRouterService(test_config.openrouter)
        
        # Test empty prompt
        with pytest.raises(ValueError, match="Prompt cannot be empty"):
            service.generate_text("")
        
        # Test too long prompt
        long_prompt = "x" * 100000
        with pytest.raises(ValueError, match="Prompt too long"):
            service.generate_text(long_prompt)
        
        # Test invalid parameters
        with pytest.raises(ValueError, match="Temperature must be between 0 and 1"):
            service.generate_text("Test prompt", temperature=2.0)
        
        with pytest.raises(ValueError, match="Max tokens must be positive"):
            service.generate_text("Test prompt", max_tokens=-1)

    def test_replicate_service_errors(self, test_config):
        """Test Replicate service error handling."""
        service = ReplicateService(test_config.replicate)
        
        # Test empty prompt
        with pytest.raises(ValueError, match="Image prompt cannot be empty"):
            service.generate_image("")
        
        # Test too long prompt
        long_prompt = "x" * 1000
        with pytest.raises(ValueError, match="Image prompt too long"):
            service.generate_image(long_prompt)
        
        # Test invalid dimensions
        with pytest.raises(ValueError, match="Width must be between 256 and 1536"):
            service.generate_image("Test prompt", width=100)
        
        with pytest.raises(ValueError, match="Height must be between 256 and 1536"):
            service.generate_image("Test prompt", height=2000)

    def test_brave_search_service_errors(self, test_config):
        """Test Brave Search service error handling."""
        service = BraveSearchService(test_config.brave_search)
        
        # Test empty query
        with pytest.raises(ValueError, match="Search query cannot be empty"):
            service.search("")
        
        # Test too long query
        long_query = "x" * 1000
        with pytest.raises(ValueError, match="Search query too long"):
            service.search(long_query)
        
        # Test invalid max_results
        with pytest.raises(ValueError, match="Max results must be between 1 and 50"):
            service.search("test query", max_results=0)

    def test_template_service_errors(self):
        """Test Template service error handling."""
        service = TemplateService()
        
        # Test non-existent template
        with pytest.raises(FileNotFoundError):
            service.load_template("nonexistent_template.md")
        
        # Test empty template
        with pytest.raises(ValueError, match="Template cannot be empty"):
            service.validate_template("")
        
        # Test invalid template rendering
        with pytest.raises(Exception):
            service.render_template("{{ invalid_template }}", {})

    def test_file_structure_service_errors(self):
        """Test File Structure service error handling."""
        service = FileStructureService()
        
        # Test non-existent directory
        with pytest.raises(ValueError, match="Directory does not exist"):
            service.validate_directory(Path("/nonexistent/directory"))
        
        # Test directory info on non-existent directory
        with pytest.raises(ValueError):
            service.get_directory_info(Path("/nonexistent/directory"))

    def test_input_processor_errors(self):
        """Test Input Processor error handling."""
        processor = InputProcessor()
        
        # Test empty content
        with pytest.raises(ValueError, match="Note content cannot be empty"):
            processor.parse_note("", "test.md", "markdown")
        
        # Test invalid file type
        with pytest.raises(ValueError, match="Unsupported file type"):
            processor.parse_note("content", "test.pdf", "pdf")
        
        # Test non-existent inbox directory
        processor.inbox_dir = Path("/nonexistent/inbox")
        with pytest.raises(ValueError):
            processor.scan_inbox()

    def test_output_generator_errors(self):
        """Test Output Generator error handling."""
        generator = OutputGenerator()
        
        # Test non-existent output directory
        generator.output_dir = Path("/nonexistent/output")
        blog_post = BlogPost(
            title="Test Post",
            description="Test description",
            content="# Test Post\n\nContent here.",
            category="development",
            tags=["test", "blog"]
        )
        
        with pytest.raises(ValueError):
            generator.generate_markdown_file(blog_post)
        
        # Test invalid output validation
        with pytest.raises(ValueError, match="Output file does not exist"):
            generator.validate_output(Path("/nonexistent/file.md"))


class TestAgentErrorHandling:
    """Test error handling in agents."""
    
    def test_base_agent_errors(self, test_config):
        """Test Base Agent error handling."""
        agent = BaseAgent(
            name="test_agent",
            role="Test Role",
            goal="Test Goal",
            config=test_config
        )
        
        # Test empty input validation
        with pytest.raises(ValueError, match="Input cannot be empty"):
            agent.validate_input("")
        
        # Test non-existent template
        with pytest.raises(FileNotFoundError):
            agent.load_prompt_template("nonexistent_template.txt")

    def test_content_analyzer_errors(self, test_config):
        """Test Content Analyzer error handling."""
        agent = ContentAnalyzer(test_config)
        
        # Test invalid analysis result
        invalid_result = {
            "description": "Test Description",
            "outline": ["Section 1", "Section 2"]
        }
        with pytest.raises(ValueError, match="Analysis result missing required fields"):
            agent.validate_analysis_result(invalid_result)
        
        # Test empty note content
        empty_note = Note(
            content="",
            source_file="test.md",
            file_type="markdown"
        )
        with pytest.raises(ValueError):
            agent.analyze_note(empty_note)

    def test_agent_recovery_mechanisms(self, test_config):
        """Test agent recovery mechanisms."""
        agent = ContentAnalyzer(test_config)
        
        # Test with invalid config
        with patch.object(agent, 'config', None):
            with pytest.raises(AttributeError):
                agent.analyze_note(Mock())


class TestCrewErrorHandling:
    """Test error handling in crews."""
    
    def test_blog_post_crew_errors(self, test_config):
        """Test Blog Post Crew error handling."""
        crew = BlogPostCrew(test_config)
        
        # Test with invalid note
        with pytest.raises(ValueError):
            crew.process_note(None)
        
        # Test with empty note
        empty_note = Note(
            content="",
            source_file="test.md",
            file_type="markdown"
        )
        with pytest.raises(ValueError):
            crew.process_note(empty_note)

    def test_crew_recovery_mechanisms(self, test_config):
        """Test crew recovery mechanisms."""
        crew = BlogPostCrew(test_config)
        
        # Test with missing agents
        with patch.object(crew, 'content_analyzer', None):
            with pytest.raises(AttributeError):
                crew.process_note(Mock())


class TestModelErrorHandling:
    """Test error handling in data models."""
    
    def test_blog_post_validation_errors(self):
        """Test BlogPost validation errors."""
        # Test empty title
        with pytest.raises(ValueError, match="Title cannot be empty"):
            BlogPost(
                title="",
                description="Test description",
                content="# Test Post\n\nContent here.",
                category="development",
                tags=["test", "blog"]
            )
        
        # Test invalid category
        with pytest.raises(ValueError, match="Invalid category"):
            BlogPost(
                title="Test Post",
                description="Test description",
                content="# Test Post\n\nContent here.",
                category="invalid-category",
                tags=["test", "blog"]
            )
        
        # Test too many tags
        with pytest.raises(ValueError, match="Too many tags"):
            BlogPost(
                title="Test Post",
                description="Test description",
                content="# Test Post\n\nContent here.",
                category="development",
                tags=["tag"] * 10
            )
        
        # Test too few tags
        with pytest.raises(ValueError, match="Too few tags"):
            BlogPost(
                title="Test Post",
                description="Test description",
                content="# Test Post\n\nContent here.",
                category="development",
                tags=["tag"]
            )

    def test_note_validation_errors(self):
        """Test Note validation errors."""
        # Test empty content
        with pytest.raises(ValueError, match="Content cannot be empty"):
            Note(
                content="",
                source_file="test.md",
                file_type="markdown"
            )
        
        # Test invalid file type
        with pytest.raises(ValueError, match="Unsupported file type"):
            Note(
                content="Test content",
                source_file="test.pdf",
                file_type="pdf"
            )


class TestGracefulDegradation:
    """Test graceful degradation scenarios."""
    
    def test_service_unavailable_handling(self, test_config):
        """Test handling when services are unavailable."""
        # Test OpenRouter service unavailable
        with patch('src.services.openrouter_service.OpenRouterService') as mock_service:
            mock_service.side_effect = Exception("Service unavailable")
            
            with pytest.raises(Exception, match="Service unavailable"):
                OpenRouterService(test_config.openrouter)
    
    def test_partial_failure_handling(self, test_config):
        """Test handling of partial failures."""
        # Test when some agents fail but others succeed
        crew = BlogPostCrew(test_config)
        
        with patch.object(crew.content_analyzer, 'analyze_note') as mock_analyze:
            mock_analyze.side_effect = Exception("Analysis failed")
            
            note = Note(
                content="Test content",
                source_file="test.md",
                file_type="markdown"
            )
            
            with pytest.raises(Exception, match="Analysis failed"):
                crew.process_note(note)

    def test_resource_limitation_handling(self, test_config):
        """Test handling of resource limitations."""
        # Test when disk space is limited
        with patch('pathlib.Path.stat') as mock_stat:
            mock_stat.return_value = Mock(st_size=0)  # No space available
            
            generator = OutputGenerator()
            blog_post = BlogPost(
                title="Test Post",
                description="Test description",
                content="# Test Post\n\nContent here.",
                category="development",
                tags=["test", "blog"]
            )
            
            # Should handle gracefully or raise appropriate error
            with pytest.raises(Exception):
                generator.generate_markdown_file(blog_post)

    def test_network_failure_handling(self, test_config):
        """Test handling of network failures."""
        # Test when network is unavailable
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.side_effect = Exception("Network error")
            
            service = BraveSearchService(test_config.brave_search)
            
            with pytest.raises(Exception, match="Network error"):
                service.search("test query")


class TestErrorLogging:
    """Test error logging functionality."""
    
    def test_error_logging_format(self, test_config):
        """Test error logging format."""
        service = OpenRouterService(test_config.openrouter)
        
        # Test that errors are logged with proper format
        with patch('logging.Logger.error') as mock_logger:
            try:
                service.generate_text("")
            except ValueError:
                pass
            
            # Verify error was logged
            mock_logger.assert_called()
            call_args = mock_logger.call_args[0][0]
            assert "function" in call_args.lower()
            assert "line" in call_args.lower()

    def test_error_context_preservation(self, test_config):
        """Test that error context is preserved."""
        service = OpenRouterService(test_config.openrouter)
        
        # Test that original error context is preserved
        with pytest.raises(ValueError) as exc_info:
            service.generate_text("")
        
        assert "Prompt cannot be empty" in str(exc_info.value)

    def test_error_recovery_logging(self, test_config):
        """Test error recovery logging."""
        service = OpenRouterService(test_config.openrouter)
        
        # Test that recovery attempts are logged
        with patch('logging.Logger.info') as mock_logger:
            try:
                service.generate_text("")
            except ValueError:
                pass
            
            # Verify recovery attempt was logged
            mock_logger.assert_called()


class TestPerformanceUnderError:
    """Test performance under error conditions."""
    
    def test_error_performance_impact(self, test_config):
        """Test that errors don't significantly impact performance."""
        import time
        
        service = OpenRouterService(test_config.openrouter)
        
        start_time = time.time()
        
        # Generate multiple errors quickly
        for _ in range(10):
            try:
                service.generate_text("")
            except ValueError:
                pass
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should handle errors quickly (less than 1 second for 10 errors)
        assert processing_time < 1.0

    def test_concurrent_error_handling(self, test_config):
        """Test concurrent error handling."""
        import threading
        import time
        
        service = OpenRouterService(test_config.openrouter)
        errors = []
        
        def generate_error():
            try:
                service.generate_text("")
            except ValueError as e:
                errors.append(e)
        
        # Start multiple threads generating errors
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=generate_error)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Should handle all errors without crashing
        assert len(errors) == 5 