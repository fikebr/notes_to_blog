"""
Unit tests for agents.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path

from src.agents.base_agent import BaseAgent
from src.agents.content_analyzer import ContentAnalyzer
from src.agents.researcher import Researcher
from src.agents.content_writer import ContentWriter
from src.agents.image_generator import ImageGenerator
from src.agents.metadata_generator import MetadataGenerator
from src.models.blog_models import Note, BlogPost, Image


class TestBaseAgent:
    """Test base agent functionality."""
    
    def test_init(self, test_config):
        """Test agent initialization."""
        agent = BaseAgent(
            name="test_agent",
            role="Test Role",
            goal="Test Goal",
            config=test_config
        )
        assert agent.name == "test_agent"
        assert agent.role == "Test Role"
        assert agent.goal == "Test Goal"
        assert agent.config == test_config

    def test_load_prompt_template(self, test_config):
        """Test prompt template loading."""
        agent = BaseAgent(
            name="test_agent",
            role="Test Role",
            goal="Test Goal",
            config=test_config
        )
        
        # Test with existing template
        template = agent.load_prompt_template("content_analyzer.txt")
        assert template is not None
        assert "{{ note_content }}" in template

    def test_load_prompt_template_not_found(self, test_config):
        """Test prompt template loading when file not found."""
        agent = BaseAgent(
            name="test_agent",
            role="Test Role",
            goal="Test Goal",
            config=test_config
        )
        
        with pytest.raises(FileNotFoundError):
            agent.load_prompt_template("nonexistent_template.txt")

    def test_render_prompt(self, test_config):
        """Test prompt rendering."""
        agent = BaseAgent(
            name="test_agent",
            role="Test Role",
            goal="Test Goal",
            config=test_config
        )
        
        template = "Hello {{ name }}! Your role is {{ role }}."
        context = {"name": "Agent", "role": "Tester"}
        
        result = agent.render_prompt(template, context)
        assert result == "Hello Agent! Your role is Tester."

    def test_validate_input(self, test_config):
        """Test input validation."""
        agent = BaseAgent(
            name="test_agent",
            role="Test Role",
            goal="Test Goal",
            config=test_config
        )
        
        # Valid input
        assert agent.validate_input("Valid input") is True
        
        # Empty input
        with pytest.raises(ValueError):
            agent.validate_input("")

    def test_log_activity(self, test_config):
        """Test activity logging."""
        agent = BaseAgent(
            name="test_agent",
            role="Test Role",
            goal="Test Goal",
            config=test_config
        )
        
        # Should not raise any exceptions
        agent.log_activity("Test activity", "info")


class TestContentAnalyzer:
    """Test Content Analyzer agent."""
    
    def test_init(self, test_config):
        """Test agent initialization."""
        agent = ContentAnalyzer(test_config)
        assert agent.name == "content_analyzer"
        assert agent.role == "Content Analysis Specialist"
        assert "analyze" in agent.goal.lower()

    def test_analyze_note(self, test_config, mock_openrouter_service, sample_note_content):
        """Test note analysis."""
        agent = ContentAnalyzer(test_config)
        
        note = Note(
            content=sample_note_content,
            source_file="test.md",
            file_type="markdown"
        )
        
        result = agent.analyze_note(note)
        assert result is not None
        assert isinstance(result, dict)

    def test_generate_title(self, test_config, mock_openrouter_service):
        """Test title generation."""
        agent = ContentAnalyzer(test_config)
        
        result = agent.generate_title("Test note content")
        assert result is not None
        assert isinstance(result, str)

    def test_generate_description(self, test_config, mock_openrouter_service):
        """Test description generation."""
        agent = ContentAnalyzer(test_config)
        
        result = agent.generate_description("Test note content")
        assert result is not None
        assert isinstance(result, str)

    def test_generate_outline(self, test_config, mock_openrouter_service):
        """Test outline generation."""
        agent = ContentAnalyzer(test_config)
        
        result = agent.generate_outline("Test note content")
        assert result is not None
        assert isinstance(result, list)
        assert len(result) >= 2
        assert len(result) <= 5

    def test_validate_analysis_result(self, test_config):
        """Test analysis result validation."""
        agent = ContentAnalyzer(test_config)
        
        # Valid result
        valid_result = {
            "title": "Test Title",
            "description": "Test Description",
            "outline": ["Section 1", "Section 2"]
        }
        assert agent.validate_analysis_result(valid_result) is True
        
        # Invalid result (missing title)
        invalid_result = {
            "description": "Test Description",
            "outline": ["Section 1", "Section 2"]
        }
        with pytest.raises(ValueError):
            agent.validate_analysis_result(invalid_result)


class TestResearcher:
    """Test Researcher agent."""
    
    def test_init(self, test_config):
        """Test agent initialization."""
        agent = Researcher(test_config)
        assert agent.name == "researcher"
        assert agent.role == "Research Specialist"
        assert "research" in agent.goal.lower()

    def test_research_topic(self, test_config, mock_brave_search_service):
        """Test topic research."""
        agent = Researcher(test_config)
        
        result = agent.research_topic("Python programming")
        assert result is not None
        assert isinstance(result, dict)
        assert "results" in result

    def test_research_subheading(self, test_config, mock_brave_search_service):
        """Test subheading research."""
        agent = Researcher(test_config)
        
        result = agent.research_subheading("Python functions", "Functions in Python")
        assert result is not None
        assert isinstance(result, dict)

    def test_validate_sources(self, test_config):
        """Test source validation."""
        agent = Researcher(test_config)
        
        sources = [
            {"title": "Source 1", "url": "https://example.com/1", "description": "Desc 1"},
            {"title": "Source 2", "url": "https://example.com/2", "description": "Desc 2"}
        ]
        
        valid_sources = agent.validate_sources(sources)
        assert len(valid_sources) == 2

    def test_filter_relevant_results(self, test_config):
        """Test result filtering."""
        agent = Researcher(test_config)
        
        results = [
            {"title": "Relevant Result", "url": "https://example.com/1", "description": "Python programming"},
            {"title": "Irrelevant Result", "url": "https://example.com/2", "description": "Cooking recipes"}
        ]
        
        filtered = agent.filter_relevant_results(results, "Python programming")
        assert len(filtered) == 1
        assert filtered[0]["title"] == "Relevant Result"

    def test_generate_citations(self, test_config):
        """Test citation generation."""
        agent = Researcher(test_config)
        
        sources = [
            {"title": "Source 1", "url": "https://example.com/1", "description": "Desc 1"}
        ]
        
        citations = agent.generate_citations(sources)
        assert isinstance(citations, list)
        assert len(citations) == 1


class TestContentWriter:
    """Test Content Writer agent."""
    
    def test_init(self, test_config):
        """Test agent initialization."""
        agent = ContentWriter(test_config)
        assert agent.name == "content_writer"
        assert agent.role == "Content Writer"
        assert "write" in agent.goal.lower()

    def test_write_introduction(self, test_config, mock_openrouter_service):
        """Test introduction writing."""
        agent = ContentWriter(test_config)
        
        result = agent.write_introduction("Test topic", "Test description")
        assert result is not None
        assert isinstance(result, str)

    def test_write_conclusion(self, test_config, mock_openrouter_service):
        """Test conclusion writing."""
        agent = ContentWriter(test_config)
        
        result = agent.write_conclusion("Test content", "Test topic")
        assert result is not None
        assert isinstance(result, str)

    def test_write_subheading_content(self, test_config, mock_openrouter_service):
        """Test subheading content writing."""
        agent = ContentWriter(test_config)
        
        result = agent.write_subheading_content(
            "Test Subheading",
            "Test research data",
            "Test outline"
        )
        assert result is not None
        assert isinstance(result, str)

    def test_structure_content(self, test_config):
        """Test content structuring."""
        agent = ContentWriter(test_config)
        
        introduction = "Test introduction"
        subheadings = [
            {"title": "Section 1", "content": "Content 1"},
            {"title": "Section 2", "content": "Content 2"}
        ]
        conclusion = "Test conclusion"
        
        structured = agent.structure_content(introduction, subheadings, conclusion)
        assert structured is not None
        assert "Test introduction" in structured
        assert "Section 1" in structured
        assert "Section 2" in structured
        assert "Test conclusion" in structured

    def test_format_content(self, test_config):
        """Test content formatting."""
        agent = ContentWriter(test_config)
        
        content = "Test content with **bold** and *italic* text."
        formatted = agent.format_content(content)
        assert formatted is not None
        assert "**bold**" in formatted

    def test_validate_content(self, test_config):
        """Test content validation."""
        agent = ContentWriter(test_config)
        
        # Valid content
        valid_content = "# Test Post\n\nThis is valid content with sufficient length."
        assert agent.validate_content(valid_content) is True
        
        # Invalid content (too short)
        invalid_content = "Short"
        with pytest.raises(ValueError):
            agent.validate_content(invalid_content)


class TestImageGenerator:
    """Test Image Generator agent."""
    
    def test_init(self, test_config):
        """Test agent initialization."""
        agent = ImageGenerator(test_config)
        assert agent.name == "image_generator"
        assert agent.role == "Image Generation Specialist"
        assert "image" in agent.goal.lower()

    def test_generate_header_image_prompt(self, test_config, mock_openrouter_service):
        """Test header image prompt generation."""
        agent = ImageGenerator(test_config)
        
        result = agent.generate_header_image_prompt("Test blog post", "Test description")
        assert result is not None
        assert isinstance(result, str)

    def test_generate_supplemental_image_prompt(self, test_config, mock_openrouter_service):
        """Test supplemental image prompt generation."""
        agent = ImageGenerator(test_config)
        
        result = agent.generate_supplemental_image_prompt("Test section", "Test content")
        assert result is not None
        assert isinstance(result, str)

    def test_generate_image(self, test_config, mock_replicate_service):
        """Test image generation."""
        agent = ImageGenerator(test_config)
        
        result = agent.generate_image("Test image prompt")
        assert result is not None
        assert isinstance(result, dict)
        assert "url" in result

    def test_validate_image_prompt(self, test_config):
        """Test image prompt validation."""
        agent = ImageGenerator(test_config)
        
        # Valid prompt
        valid_prompt = "A beautiful landscape with mountains and trees"
        assert agent.validate_image_prompt(valid_prompt) is True
        
        # Invalid prompt (too short)
        invalid_prompt = "Short"
        with pytest.raises(ValueError):
            agent.validate_image_prompt(invalid_prompt)

    def test_optimize_prompt_for_image_generation(self, test_config):
        """Test prompt optimization."""
        agent = ImageGenerator(test_config)
        
        original_prompt = "A simple image"
        optimized = agent.optimize_prompt_for_image_generation(original_prompt)
        assert optimized is not None
        assert len(optimized) > len(original_prompt)

    def test_generate_alt_text(self, test_config, mock_openrouter_service):
        """Test alt text generation."""
        agent = ImageGenerator(test_config)
        
        result = agent.generate_alt_text("Test image prompt")
        assert result is not None
        assert isinstance(result, str)

    def test_generate_caption(self, test_config, mock_openrouter_service):
        """Test caption generation."""
        agent = ImageGenerator(test_config)
        
        result = agent.generate_caption("Test image prompt", "Test context")
        assert result is not None
        assert isinstance(result, str)


class TestMetadataGenerator:
    """Test Metadata Generator agent."""
    
    def test_init(self, test_config):
        """Test agent initialization."""
        agent = MetadataGenerator(test_config)
        assert agent.name == "metadata_generator"
        assert agent.role == "Metadata Specialist"
        assert "metadata" in agent.goal.lower()

    def test_select_category(self, test_config, mock_openrouter_service):
        """Test category selection."""
        agent = MetadataGenerator(test_config)
        
        result = agent.select_category("Test content about Python programming")
        assert result is not None
        assert isinstance(result, str)
        assert result in ["development", "computer", "ai", "business", "home", "crafting", "health", "diy", "recipes"]

    def test_generate_tags(self, test_config, mock_openrouter_service):
        """Test tag generation."""
        agent = MetadataGenerator(test_config)
        
        result = agent.generate_tags("Test content", "development")
        assert result is not None
        assert isinstance(result, list)
        assert len(result) >= 2
        assert len(result) <= 5

    def test_generate_frontmatter(self, test_config):
        """Test frontmatter generation."""
        agent = MetadataGenerator(test_config)
        
        blog_post = BlogPost(
            title="Test Post",
            description="Test description",
            content="# Test Post\n\nContent here.",
            category="development",
            tags=["test", "blog"]
        )
        
        frontmatter = agent.generate_frontmatter(blog_post)
        assert frontmatter is not None
        assert isinstance(frontmatter, str)
        assert "+++" in frontmatter
        assert "title = \"Test Post\"" in frontmatter

    def test_generate_filename(self, test_config):
        """Test filename generation."""
        agent = MetadataGenerator(test_config)
        
        result = agent.generate_filename("Test Blog Post Title")
        assert result is not None
        assert isinstance(result, str)
        assert result.startswith("test-blog-post-title")
        assert result.endswith(".md")

    def test_validate_category(self, test_config):
        """Test category validation."""
        agent = MetadataGenerator(test_config)
        
        # Valid categories
        assert agent.validate_category("development") is True
        assert agent.validate_category("ai") is True
        
        # Invalid category
        with pytest.raises(ValueError):
            agent.validate_category("invalid-category")

    def test_validate_tags(self, test_config):
        """Test tag validation."""
        agent = MetadataGenerator(test_config)
        
        # Valid tags
        valid_tags = ["python", "programming", "tutorial"]
        assert agent.validate_tags(valid_tags) is True
        
        # Too many tags
        too_many_tags = ["tag"] * 10
        with pytest.raises(ValueError):
            agent.validate_tags(too_many_tags)
        
        # Too few tags
        too_few_tags = ["tag"]
        with pytest.raises(ValueError):
            agent.validate_tags(too_few_tags)

    def test_optimize_tags(self, test_config):
        """Test tag optimization."""
        agent = MetadataGenerator(test_config)
        
        tags = ["python", "programming", "tutorial", "code", "development"]
        optimized = agent.optimize_tags(tags)
        assert len(optimized) <= 5
        assert all(isinstance(tag, str) for tag in optimized)

    def test_generate_seo_description(self, test_config, mock_openrouter_service):
        """Test SEO description generation."""
        agent = MetadataGenerator(test_config)
        
        result = agent.generate_seo_description("Test content", "Test title")
        assert result is not None
        assert isinstance(result, str)
        assert len(result) <= 160  # SEO best practice 