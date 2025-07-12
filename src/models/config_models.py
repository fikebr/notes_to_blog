"""
Configuration models for the Notes to Blog application.

This module contains all Pydantic models related to application configuration.
"""

from pathlib import Path
from typing import List

from pydantic import BaseModel, Field, field_validator


class APIConfig(BaseModel):
    """API configuration for external services."""
    
    # OpenRouter Configuration
    openrouter_api_key: str = Field(
        default="your_openrouter_api_key_here", 
        description="OpenRouter API key for LLM access"
    )
    openrouter_base_url: str = Field(
        default="https://openrouter.ai/api/v1",
        description="OpenRouter API base URL"
    )
    openrouter_model: str = Field(
        default="", 
        description="OpenRouter model to use (e.g., openai/gpt-4, anthropic/claude-3-opus, etc.)"
    )
    
    # Replicate.com Configuration
    replicate_api_token: str = Field(
        default="your_replicate_api_token_here", 
        description="Replicate.com API token for image generation"
    )
    
    # Brave Browser API Configuration
    brave_api_key: str = Field(
        default="your_brave_api_key_here", 
        description="Brave Browser API key for web search"
    )
    brave_search_url: str = Field(
        default="https://api.search.brave.com/res/v1/web/search",
        description="Brave search API URL"
    )
    
    @field_validator('openrouter_api_key', 'replicate_api_token', 'brave_api_key', mode='after')
    def validate_api_keys(cls, v: str, info):
        """Validate that API keys are not placeholder values."""
        field_name = info.field_name
        if v.startswith('your_') and v.endswith('_here'):
            raise ValueError(
                f"{field_name} is not configured. Please set the {field_name} environment variable "
                f"or add it to your .env file. See example.env.txt for details."
            )
        return v
    
    @field_validator('openrouter_model', mode='after')
    def validate_openrouter_model(cls, v: str):
        """Validate that OpenRouter model is configured."""
        if not v or v.strip() == "":
            raise ValueError(
                "openrouter_model is not configured. Please set the OPENROUTER_MODEL environment variable "
                "or add it to your .env file. See example.env.txt for details."
            )
        return v


class AppConfig(BaseModel):
    """Application settings configuration."""
    
    app_name: str = Field(default="Notes to Blog", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    app_env: str = Field(default="development", description="Environment (development/staging/production)")
    debug: bool = Field(default=True, description="Enable debug mode")


class PathConfig(BaseModel):
    """File path configuration."""
    
    inbox_dir: Path = Field(default=Path("./inbox"), description="Directory for input notes")
    output_dir: Path = Field(default=Path("./output"), description="Directory for generated blog posts")
    images_dir: Path = Field(default=Path("./images"), description="Directory for generated images")
    templates_dir: Path = Field(default=Path("./templates"), description="Directory for templates")
    log_file: Path = Field(default=Path("./logs/app.log"), description="Log file path")
    
    @field_validator('inbox_dir', 'output_dir', 'images_dir', 'templates_dir', 'log_file', mode='after')
    def ensure_directories_exist(cls, v: Path):
        """Ensure directories exist, create if they don't."""
        if v.suffix == '':  # Directory
            v.mkdir(parents=True, exist_ok=True)
        else:  # File
            v.parent.mkdir(parents=True, exist_ok=True)
        return v


class LoggingConfig(BaseModel):
    """Logging configuration."""
    
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
        description="Log format string"
    )
    log_max_size: int = Field(default=10_485_760, description="Max log file size in bytes (10MB)")
    log_backup_count: int = Field(default=3, description="Number of backup log files")


class ContentConfig(BaseModel):
    """Content generation configuration."""
    
    default_categories: List[str] = Field(
        default=["development", "computer", "home", "ai", "business", "crafting", "health", "diy", "recipes"],
        description="Available blog post categories"
    )
    max_subheadings: int = Field(default=5, description="Maximum number of subheadings")
    min_subheadings: int = Field(default=2, description="Minimum number of subheadings")
    max_tags: int = Field(default=5, description="Maximum number of tags")
    min_tags: int = Field(default=2, description="Minimum number of tags")
    
    @field_validator('min_subheadings', 'max_subheadings', mode='after')
    def validate_subheadings(cls, v, info):
        values = info.data
        if 'max_subheadings' in values and v > values['max_subheadings']:
            raise ValueError("min_subheadings cannot be greater than max_subheadings")
        if v < 1:
            raise ValueError("Subheadings must be at least 1")
        return v
    
    @field_validator('min_tags', 'max_tags', mode='after')
    def validate_tags(cls, v, info):
        values = info.data
        if 'max_tags' in values and v > values['max_tags']:
            raise ValueError("min_tags cannot be greater than max_tags")
        if v < 1:
            raise ValueError("Tags must be at least 1")
        return v


class ImageConfig(BaseModel):
    """Image generation configuration."""
    
    image_model: str = Field(
        default="stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
        description="Replicate model for image generation"
    )
    image_width: int = Field(default=1024, description="Generated image width")
    image_height: int = Field(default=1024, description="Generated image height")
    max_images_per_post: int = Field(default=5, description="Maximum images per blog post")
    
    @field_validator('image_width', 'image_height', mode='after')
    def validate_image_dimensions(cls, v):
        if v < 256 or v > 2048:
            raise ValueError("Image dimensions must be between 256 and 2048")
        return v


class QualityConfig(BaseModel):
    """Content quality configuration."""
    
    min_content_length: int = Field(default=500, description="Minimum content length in characters")
    max_content_length: int = Field(default=5000, description="Maximum content length in characters")
    research_timeout: int = Field(default=300, description="Research timeout in seconds")
    generation_timeout: int = Field(default=600, description="Content generation timeout in seconds")
    
    @field_validator('min_content_length', 'max_content_length', mode='after')
    def validate_content_length(cls, v, info):
        values = info.data
        if 'max_content_length' in values and v > values['max_content_length']:
            raise ValueError("min_content_length cannot be greater than max_content_length")
        if v < 100:
            raise ValueError("Content length must be at least 100 characters")
        return v


class CrewAIConfig(BaseModel):
    """CrewAI agent configuration."""
    
    agent_verbose: bool = Field(default=True, description="Enable verbose agent output")
    agent_memory: bool = Field(default=True, description="Enable agent memory")
    agent_max_iterations: int = Field(default=10, description="Maximum agent iterations")
    agent_temperature: float = Field(default=0.7, description="Agent temperature (0.0-1.0)")
    enable_parallel_processing: bool = Field(default=True, description="Enable parallel task processing")
    max_concurrent_tasks: int = Field(default=3, description="Maximum concurrent tasks")
    agent_max_retries: int = Field(default=3, description="Maximum retries for agent API calls")
    
    @field_validator('agent_temperature', mode='after')
    def validate_temperature(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError("Temperature must be between 0.0 and 1.0")
        return v


class StorageConfig(BaseModel):
    """Storage configuration."""
    
    pickledb_file: Path = Field(default=Path("./data/app.db"), description="PickleDB file path")
    pickledb_auto_dump: bool = Field(default=True, description="Auto-dump PickleDB changes")
    cache_enabled: bool = Field(default=True, description="Enable caching")
    cache_ttl: int = Field(default=3600, description="Cache TTL in seconds")
    cache_max_size: int = Field(default=1000, description="Maximum cache entries")
    
    @field_validator('pickledb_file', mode='after')
    def ensure_data_directory(cls, v: Path):
        v.parent.mkdir(parents=True, exist_ok=True)
        return v


class SecurityConfig(BaseModel):
    """Security and rate limiting configuration."""
    
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_requests_per_minute: int = Field(default=60, description="Requests per minute limit")
    rate_limit_requests_per_hour: int = Field(default=1000, description="Requests per hour limit")
    request_timeout: int = Field(default=30, description="Request timeout in seconds")
    connect_timeout: int = Field(default=10, description="Connection timeout in seconds")


class DevelopmentConfig(BaseModel):
    """Development and testing configuration."""
    
    test_mode: bool = Field(default=False, description="Enable test mode")
    mock_external_apis: bool = Field(default=False, description="Mock external API calls")
    test_data_dir: Path = Field(default=Path("./tests/data"), description="Test data directory")
    enable_profiling: bool = Field(default=False, description="Enable performance profiling")
    enable_debug_endpoints: bool = Field(default=False, description="Enable debug API endpoints")


class Config(BaseModel):
    """Main configuration class that combines all configuration sections."""
    
    api: APIConfig = Field(default_factory=APIConfig)
    app: AppConfig = Field(default_factory=AppConfig)
    paths: PathConfig = Field(default_factory=PathConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    content: ContentConfig = Field(default_factory=ContentConfig)
    image: ImageConfig = Field(default_factory=ImageConfig)
    quality: QualityConfig = Field(default_factory=QualityConfig)
    crewai: CrewAIConfig = Field(default_factory=CrewAIConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    development: DevelopmentConfig = Field(default_factory=DevelopmentConfig)
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore" 