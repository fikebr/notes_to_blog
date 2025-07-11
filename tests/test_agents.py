"""
Tests for CrewAI agents.

Tests all agent implementations including base agent functionality,
content analysis, research, content writing, image generation, and metadata generation.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import json

from src.agents import (
    BaseAgent, ContentAnalyzerAgent, ResearchAgent, ContentWriterAgent,
    ImageGeneratorAgent, MetadataGeneratorAgent
)
from src.models.config_models import Config
from src.services import ServiceRegistry


class TestBaseAgent:
    """Test base agent functionality."""
    
    @pytest.fixture
    def mock_config(self):
        """Create mock configuration."""
        config = Mock(spec=Config)
        config.crewai.agent_verbose = True
        config.crewai.agent_max_iterations = 3
        config.crewai.agent_memory = True
        return config
    
    @pytest.fixture
    def mock_service_registry(self):
        """Create mock service registry."""
        registry = Mock(spec=ServiceRegistry)
        openrouter_service = Mock()
        openrouter_service.create_crewai_adapter.return_value = Mock()
        registry.get_openrouter.return_value = openrouter_service
        return registry
    
    @pytest.fixture
    def base_agent(self, mock_config, mock_service_registry):
        """Create a concrete base agent for testing."""
        class TestAgent(BaseAgent):
            def _get_agent_config(self):
                from src.agents.base_agent import AgentConfig
                return AgentConfig(
                    name="Test Agent",
                    role="Test Role",
                    goal="Test goal",
                    backstory="Test backstory"
                )
            
            def _get_prompt_template_path(self):
                return Path("templates/agent_prompts/test.txt")
            
            def _get_default_prompt_template(self):
                return "Test template: {task_description}"
        
        return TestAgent(mock_config, mock_service_registry)
    
    def test_base_agent_initialization(self, base_agent):
        """Test base agent initialization."""
        assert base_agent.config is not None
        assert base_agent.service_registry is not None
        assert base_agent.agent_config.name == "Test Agent"
        assert base_agent.prompt_template == "Test template: {task_description}"
        assert base_agent.crewai_agent is not None
    
    def test_render_prompt(self, base_agent):
        """Test prompt rendering."""
        result = base_agent.render_prompt(task_description="Test task")
        assert "Test task" in result
        assert result.startswith("Test template:")
    
    def test_render_prompt_with_kwargs(self, base_agent):
        """Test prompt rendering with additional kwargs."""
        result = base_agent.render_prompt(
            task_description="Test task",
            extra_var="extra value"
        )
        assert "Test task" in result
    
    def test_health_check(self, base_agent):
        """Test agent health check."""
        health = base_agent.health_check()
        assert health["name"] == "Test Agent"
        assert health["status"] == "healthy"
        assert health["crewai_agent_created"] is True
        assert health["prompt_template_loaded"] is True


class TestContentAnalyzerAgent:
    """Test content analyzer agent."""
    
    @pytest.fixture
    def content_analyzer(self, mock_config, mock_service_registry):
        """Create content analyzer agent."""
        return ContentAnalyzerAgent(mock_config, mock_service_registry)
    
    def test_agent_config(self, content_analyzer):
        """Test content analyzer configuration."""
        config = content_analyzer.agent_config
        assert config.name == "Content Analyzer"
        assert config.role == "Content Analysis Specialist"
        assert "outline" in config.goal.lower()
    
    def test_analyze_notes(self, content_analyzer):
        """Test notes analysis."""
        with patch.object(content_analyzer, 'execute_task') as mock_execute:
            mock_execute.return_value = json.dumps({
                "title": "Test Title",
                "description": "Test description",
                "subheadings": ["Intro", "Main", "Conclusion"],
                "analysis_notes": "Test notes"
            })
            
            result = content_analyzer.analyze_notes("Test notes content")
            
            assert result["title"] == "Test Title"
            assert result["description"] == "Test description"
            assert len(result["subheadings"]) == 3
    
    def test_generate_title(self, content_analyzer):
        """Test title generation."""
        with patch.object(content_analyzer, 'execute_task') as mock_execute:
            mock_execute.return_value = "Generated Title"
            
            result = content_analyzer.generate_title("Test notes")
            assert result == "Generated Title"
    
    def test_generate_description(self, content_analyzer):
        """Test description generation."""
        with patch.object(content_analyzer, 'execute_task') as mock_execute:
            mock_execute.return_value = "Generated description"
            
            result = content_analyzer.generate_description("Test notes")
            assert result == "Generated description"
    
    def test_generate_subheadings(self, content_analyzer):
        """Test subheading generation."""
        with patch.object(content_analyzer, 'execute_task') as mock_execute:
            mock_execute.return_value = "1. Introduction\n2. Main Content\n3. Conclusion"
            
            result = content_analyzer.generate_subheadings("Test notes", 3)
            assert len(result) == 3
            assert "Introduction" in result[0]
            assert "Main Content" in result[1]
            assert "Conclusion" in result[2]


class TestResearchAgent:
    """Test research agent."""
    
    @pytest.fixture
    def research_agent(self, mock_config, mock_service_registry):
        """Create research agent."""
        return ResearchAgent(mock_config, mock_service_registry)
    
    def test_agent_config(self, research_agent):
        """Test research agent configuration."""
        config = research_agent.agent_config
        assert config.name == "Research Specialist"
        assert config.role == "Research Specialist"
        assert "research" in config.goal.lower()
    
    def test_research_topic(self, research_agent):
        """Test topic research."""
        with patch.object(research_agent, 'execute_task') as mock_execute:
            mock_execute.return_value = """
            RESEARCH SUMMARY: Test summary
            
            KEY POINTS:
            - Point 1
            - Point 2
            
            SOURCES:
            - Source 1
            - Source 2
            
            CONTENT SUGGESTIONS: Test suggestions
            """
            
            result = research_agent.research_topic("Test topic")
            
            assert "Test summary" in result["summary"]
            assert len(result["key_points"]) == 2
            assert len(result["sources"]) == 2
    
    def test_research_subheading(self, research_agent):
        """Test subheading research."""
        with patch.object(research_agent, 'execute_task') as mock_execute:
            mock_execute.return_value = "RESEARCH SUMMARY: Test\nKEY POINTS:\n- Point 1"
            
            result = research_agent.research_subheading("Test subheading")
            
            assert result["subheading"] == "Test subheading"
            assert "Test" in result["summary"]
    
    def test_validate_sources(self, research_agent):
        """Test source validation."""
        with patch.object(research_agent, 'execute_task') as mock_execute:
            mock_execute.return_value = "Validation results"
            
            sources = ["http://example1.com", "http://example2.com"]
            result = research_agent.validate_sources(sources)
            
            assert len(result) == 2
            assert all("valid" in item for item in result)
    
    def test_generate_citations(self, research_agent):
        """Test citation generation."""
        with patch.object(research_agent, 'execute_task') as mock_execute:
            mock_execute.return_value = "- Citation 1\n- Citation 2"
            
            research_data = {"sources": ["http://example1.com", "http://example2.com"]}
            result = research_agent.generate_citations(research_data)
            
            assert len(result) == 2


class TestContentWriterAgent:
    """Test content writer agent."""
    
    @pytest.fixture
    def content_writer(self, mock_config, mock_service_registry):
        """Create content writer agent."""
        return ContentWriterAgent(mock_config, mock_service_registry)
    
    def test_agent_config(self, content_writer):
        """Test content writer configuration."""
        config = content_writer.agent_config
        assert config.name == "Content Writer"
        assert config.role == "Content Writer Specialist"
        assert "engaging" in config.goal.lower()
    
    def test_write_introduction(self, content_writer):
        """Test introduction writing."""
        with patch.object(content_writer, 'execute_task') as mock_execute:
            mock_execute.return_value = "Generated introduction"
            
            result = content_writer.write_introduction("Test Title", "Test description")
            assert result == "Generated introduction"
    
    def test_write_conclusion(self, content_writer):
        """Test conclusion writing."""
        with patch.object(content_writer, 'execute_task') as mock_execute:
            mock_execute.return_value = "Generated conclusion"
            
            result = content_writer.write_conclusion("Test Title", ["Point 1", "Point 2"])
            assert result == "Generated conclusion"
    
    def test_expand_subheading(self, content_writer):
        """Test subheading expansion."""
        with patch.object(content_writer, 'execute_task') as mock_execute:
            mock_execute.return_value = "Expanded content"
            
            research_data = {
                "summary": "Test summary",
                "key_points": ["Point 1"],
                "sources": ["Source 1"]
            }
            
            result = content_writer.expand_subheading("Test subheading", research_data)
            assert result == "Expanded content"
    
    def test_structure_content(self, content_writer):
        """Test content structuring."""
        with patch.object(content_writer, 'execute_task') as mock_execute:
            mock_execute.return_value = "Structured content"
            
            sections = {"Section 1": "Content 1", "Section 2": "Content 2"}
            result = content_writer.structure_content(sections)
            assert result == "Structured content"
    
    def test_write_complete_post(self, content_writer):
        """Test complete post writing."""
        with patch.object(content_writer, 'write_introduction') as mock_intro:
            with patch.object(content_writer, 'expand_subheading') as mock_expand:
                with patch.object(content_writer, 'write_conclusion') as mock_conclusion:
                    mock_intro.return_value = "Introduction"
                    mock_expand.return_value = "Expanded content"
                    mock_conclusion.return_value = "Conclusion"
                    
                    result = content_writer.write_complete_post(
                        "Test Title", "Test description", 
                        ["Section 1", "Section 2"], {}
                    )
                    
                    assert "Test Title" in result
                    assert "Introduction" in result
                    assert "Conclusion" in result


class TestImageGeneratorAgent:
    """Test image generator agent."""
    
    @pytest.fixture
    def image_generator(self, mock_config, mock_service_registry):
        """Create image generator agent."""
        return ImageGeneratorAgent(mock_config, mock_service_registry)
    
    def test_agent_config(self, image_generator):
        """Test image generator configuration."""
        config = image_generator.agent_config
        assert config.name == "Image Generator"
        assert config.role == "Image Generation Specialist"
        assert "visual" in config.goal.lower()
    
    def test_create_image_prompts(self, image_generator):
        """Test image prompt creation."""
        with patch.object(image_generator, 'execute_task') as mock_execute:
            mock_execute.return_value = """
            HEADER IMAGE: Header prompt
            
            SUPPLEMENTAL IMAGES:
            1. Supplemental prompt 1
            2. Supplemental prompt 2
            
            STYLE NOTES: Style guidance
            """
            
            result = image_generator.create_image_prompts(
                "Test Title", "Test content", ["Section 1", "Section 2"]
            )
            
            assert "Header prompt" in result["header_image"]
            assert len(result["supplemental_images"]) == 2
            assert "Style guidance" in result["style_notes"]
    
    def test_create_header_image_prompt(self, image_generator):
        """Test header image prompt creation."""
        with patch.object(image_generator, 'execute_task') as mock_execute:
            mock_execute.return_value = "Header image prompt"
            
            result = image_generator.create_header_image_prompt("Test Title", "Test description")
            assert result == "Header image prompt"
    
    def test_create_supplemental_image_prompts(self, image_generator):
        """Test supplemental image prompt creation."""
        with patch.object(image_generator, 'execute_task') as mock_execute:
            mock_execute.return_value = "1. Prompt 1\n2. Prompt 2"
            
            result = image_generator.create_supplemental_image_prompts(
                ["Section 1", "Section 2"], "Test content"
            )
            
            assert len(result) == 2
    
    def test_generate_images(self, image_generator, mock_service_registry):
        """Test image generation."""
        replicate_service = Mock()
        replicate_service.generate_image.return_value = "/path/to/image.jpg"
        mock_service_registry.get_replicate.return_value = replicate_service
        
        image_prompts = {
            "header_image": "Header prompt",
            "supplemental_images": ["Prompt 1", "Prompt 2"]
        }
        
        result = image_generator.generate_images(image_prompts)
        
        assert "header" in result
        assert "supplemental_1" in result
        assert "supplemental_2" in result
    
    def test_link_images_in_content(self, image_generator):
        """Test image linking in content."""
        with patch.object(image_generator, 'execute_task') as mock_execute:
            mock_execute.return_value = "Content with images"
            
            image_paths = {"header": "/path/to/header.jpg", "supplemental_1": "/path/to/supp1.jpg"}
            result = image_generator.link_images_in_content("Test content", image_paths)
            
            assert result == "Content with images"


class TestMetadataGeneratorAgent:
    """Test metadata generator agent."""
    
    @pytest.fixture
    def metadata_generator(self, mock_config, mock_service_registry):
        """Create metadata generator agent."""
        return MetadataGeneratorAgent(mock_config, mock_service_registry)
    
    def test_agent_config(self, metadata_generator):
        """Test metadata generator configuration."""
        config = metadata_generator.agent_config
        assert config.name == "Metadata Generator"
        assert config.role == "Metadata Generation Specialist"
        assert "SEO" in config.goal
    
    def test_available_categories(self, metadata_generator):
        """Test available categories."""
        categories = metadata_generator.AVAILABLE_CATEGORIES
        assert "development" in categories
        assert "ai" in categories
        assert "business" in categories
        assert len(categories) == 9
    
    def test_generate_metadata(self, metadata_generator):
        """Test metadata generation."""
        with patch.object(metadata_generator, 'execute_task') as mock_execute:
            mock_execute.return_value = json.dumps({
                "category": "development",
                "tags": ["programming", "coding"],
                "filename": "test-post.md",
                "frontmatter": {
                    "title": "Test Title",
                    "description": "Test description",
                    "date": "2025-01-27",
                    "draft": True,
                    "taxonomies": {
                        "categories": ["development"],
                        "tags": ["programming", "coding"]
                    }
                }
            })
            
            result = metadata_generator.generate_metadata("Test Title", "Test description", "Test content")
            
            assert result["category"] == "development"
            assert result["tags"] == ["programming", "coding"]
            assert result["filename"] == "test-post.md"
    
    def test_select_category(self, metadata_generator):
        """Test category selection."""
        with patch.object(metadata_generator, 'execute_task') as mock_execute:
            mock_execute.return_value = "development"
            
            result = metadata_generator.select_category("Test Title", "Test content")
            assert result == "development"
    
    def test_generate_tags(self, metadata_generator):
        """Test tag generation."""
        with patch.object(metadata_generator, 'execute_task') as mock_execute:
            mock_execute.return_value = "programming\ncoding\nsoftware"
            
            result = metadata_generator.generate_tags("Test Title", "Test content", "development")
            
            assert len(result) >= 2
            assert "programming" in result
    
    def test_generate_filename(self, metadata_generator):
        """Test filename generation."""
        with patch.object(metadata_generator, 'execute_task') as mock_execute:
            mock_execute.return_value = "test-blog-post.md"
            
            result = metadata_generator.generate_filename("Test Blog Post", "development")
            assert result == "test-blog-post.md"
    
    def test_create_frontmatter(self, metadata_generator):
        """Test frontmatter creation."""
        with patch.object(metadata_generator, 'execute_task') as mock_execute:
            mock_execute.return_value = json.dumps({
                "title": "Test Title",
                "description": "Test description",
                "date": "2025-01-27",
                "draft": True,
                "taxonomies": {
                    "categories": ["development"],
                    "tags": ["programming", "coding"]
                }
            })
            
            result = metadata_generator.create_frontmatter(
                "Test Title", "Test description", "development", ["programming", "coding"]
            )
            
            assert result["title"] == "Test Title"
            assert result["draft"] is True
            assert "development" in result["taxonomies"]["categories"]
    
    def test_clean_filename(self, metadata_generator):
        """Test filename cleaning."""
        result = metadata_generator._clean_filename("Test Blog Post!")
        assert result == "test-blog-post.md"
        
        result = metadata_generator._clean_filename("Test Post.md")
        assert result == "test-post.md"
    
    def test_determine_default_category(self, metadata_generator):
        """Test default category determination."""
        result = metadata_generator._determine_default_category("Python Programming", "Code examples")
        assert result == "development"
        
        result = metadata_generator._determine_default_category("AI and Machine Learning", "ML content")
        assert result == "ai"
    
    def test_generate_fallback_tags(self, metadata_generator):
        """Test fallback tag generation."""
        result = metadata_generator._generate_fallback_tags("development")
        assert result == ["programming", "coding", "software"]
        
        result = metadata_generator._generate_fallback_tags("ai")
        assert result == ["artificial-intelligence", "machine-learning", "automation"]


if __name__ == "__main__":
    pytest.main([__file__]) 