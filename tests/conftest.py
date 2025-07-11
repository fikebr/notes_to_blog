"""
Pytest configuration and fixtures for the Notes to Blog application.
"""
import pytest
import tempfile
import os
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
from typing import Generator

from src.models.config_models import Config, APIConfig, AppConfig, ImageConfig, LoggingConfig
from src.logger import setup_logging


@pytest.fixture(scope="session")
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="session")
def test_config() -> Config:
    """Create a test configuration."""
    return Config(
        api=APIConfig(
            openrouter_api_key="test-key",
            openrouter_base_url="https://api.openrouter.ai/api/v1",
            replicate_api_token="test-key",
            brave_api_key="test-key",
            brave_search_url="https://api.search.brave.com/res/v1/web/search"
        ),
        app=AppConfig(
            app_name="test-app",
            app_version="0.1.0",
            app_env="test",
            debug=True
        ),
        logging=LoggingConfig(
            log_level="DEBUG",
            log_format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        ),
        image=ImageConfig(
            image_model="stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
            image_width=1024,
            image_height=1024,
            max_images_per_post=5
        )
    )


@pytest.fixture(scope="session")
def test_logger():
    """Create a test logger."""
    return setup_logging(
        log_file_path="test.log",
        console_level="DEBUG",
        file_level="DEBUG"
    )


@pytest.fixture
def mock_openrouter_service():
    """Mock OpenRouter service."""
    with patch('src.services.openrouter_service.OpenRouterService') as mock:
        service = mock.return_value
        service.generate_text.return_value = "Mock generated text"
        service.generate_text_async.return_value = "Mock async generated text"
        yield service


@pytest.fixture
def mock_replicate_service():
    """Mock Replicate service."""
    with patch('src.services.replicate_service.ReplicateService') as mock:
        service = mock.return_value
        service.generate_image.return_value = {
            "id": "test-image-id",
            "url": "https://example.com/test-image.jpg",
            "status": "succeeded"
        }
        service.generate_image_async.return_value = {
            "id": "test-image-id",
            "url": "https://example.com/test-image.jpg",
            "status": "succeeded"
        }
        yield service


@pytest.fixture
def mock_brave_search_service():
    """Mock Brave Search service."""
    with patch('src.services.brave_search_service.BraveSearchService') as mock:
        service = mock.return_value
        service.search.return_value = {
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
        service.search_async.return_value = {
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
        yield service


@pytest.fixture
def sample_note_content() -> str:
    """Sample note content for testing."""
    return """
    # My Test Note
    
    This is a sample note for testing purposes.
    
    ## Key Points
    - Point 1: Important information
    - Point 2: More details
    - Point 3: Additional context
    
    ## Ideas
    Some ideas for the blog post:
    - Idea 1
    - Idea 2
    - Idea 3
    
    ## Notes
    Additional notes and thoughts.
    """


@pytest.fixture
def sample_blog_post_data() -> dict:
    """Sample blog post data for testing."""
    return {
        "title": "Test Blog Post",
        "description": "A test blog post for testing purposes",
        "content": "# Test Blog Post\n\nThis is a test blog post content.",
        "category": "development",
        "tags": ["test", "blog", "example"],
        "images": [
            {
                "url": "https://example.com/image1.jpg",
                "alt_text": "Test image 1",
                "caption": "A test image"
            }
        ]
    }


@pytest.fixture
def sample_frontmatter() -> str:
    """Sample frontmatter for testing."""
    return """+++
title = "Test Blog Post"
description = "A test blog post for testing purposes"
date = 2025-01-27
draft = true

[taxonomies]
categories=["development"]
tags=["test", "blog", "example"]
+++"""


@pytest.fixture
def mock_crewai_agent():
    """Mock CrewAI Agent."""
    agent = Mock()
    agent.execute_task.return_value = "Mock agent result"
    return agent


@pytest.fixture
def mock_crewai_crew():
    """Mock CrewAI Crew."""
    crew = Mock()
    crew.kickoff.return_value = "Mock crew result"
    return crew 