"""
Configuration management for the Notes to Blog application.

This module handles all application configuration including environment variables,
default values, and validation using Pydantic models.
"""

import os
from typing import Optional

from dotenv import load_dotenv

from src.models.config_models import Config


def load_config(env_file: Optional[str] = None) -> Config:
    """
    Load configuration from environment variables and .env file.
    
    Args:
        env_file: Optional path to .env file. Defaults to .env in current directory.
        
    Returns:
        Config: Loaded configuration object.
        
    Raises:
        ValueError: If required configuration is missing or invalid.
    """
    # Load .env file if it exists
    if env_file:
        load_dotenv(env_file)
    else:
        load_dotenv()
    
    # Validate required environment variables
    required_vars = [
        "OPENROUTER_API_KEY",
        "REPLICATE_API_TOKEN", 
        "BRAVE_API_KEY"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    # Create configuration from environment
    config_data = {
        "api": {
            "openrouter_api_key": os.getenv("OPENROUTER_API_KEY"),
            "openrouter_base_url": os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
            "replicate_api_token": os.getenv("REPLICATE_API_TOKEN"),
            "brave_api_key": os.getenv("BRAVE_API_KEY"),
            "brave_search_url": os.getenv("BRAVE_SEARCH_URL", "https://api.search.brave.com/res/v1/web/search"),
        },
        "app": {
            "app_name": os.getenv("APP_NAME", "Notes to Blog"),
            "app_version": os.getenv("APP_VERSION", "0.1.0"),
            "app_env": os.getenv("APP_ENV", "development"),
            "debug": os.getenv("DEBUG", "true").lower() == "true",
        },
        "paths": {
            "inbox_dir": os.getenv("INBOX_DIR", "./inbox"),
            "output_dir": os.getenv("OUTPUT_DIR", "./output"),
            "images_dir": os.getenv("IMAGES_DIR", "./images"),
            "templates_dir": os.getenv("TEMPLATES_DIR", "./templates"),
            "log_file": os.getenv("LOG_FILE", "./logs/app.log"),
        },
        "logging": {
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "log_format": os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"),
            "log_max_size": int(os.getenv("LOG_MAX_SIZE", "10485760")),
            "log_backup_count": int(os.getenv("LOG_BACKUP_COUNT", "3")),
        },
        "content": {
            "default_categories": os.getenv("DEFAULT_CATEGORIES", "development,computer,home,ai,business,crafting,health,diy,recipes").split(","),
            "max_subheadings": int(os.getenv("MAX_SUBHEADINGS", "5")),
            "min_subheadings": int(os.getenv("MIN_SUBHEADINGS", "2")),
            "max_tags": int(os.getenv("MAX_TAGS", "5")),
            "min_tags": int(os.getenv("MIN_TAGS", "2")),
        },
        "image": {
            "image_model": os.getenv("IMAGE_MODEL", "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b"),
            "image_width": int(os.getenv("IMAGE_WIDTH", "1024")),
            "image_height": int(os.getenv("IMAGE_HEIGHT", "1024")),
            "max_images_per_post": int(os.getenv("MAX_IMAGES_PER_POST", "5")),
        },
        "quality": {
            "min_content_length": int(os.getenv("MIN_CONTENT_LENGTH", "500")),
            "max_content_length": int(os.getenv("MAX_CONTENT_LENGTH", "5000")),
            "research_timeout": int(os.getenv("RESEARCH_TIMEOUT", "300")),
            "generation_timeout": int(os.getenv("GENERATION_TIMEOUT", "600")),
        },
        "crewai": {
            "agent_verbose": os.getenv("AGENT_VERBOSE", "true").lower() == "true",
            "agent_memory": os.getenv("AGENT_MEMORY", "true").lower() == "true",
            "agent_max_iterations": int(os.getenv("AGENT_MAX_ITERATIONS", "10")),
            "agent_temperature": float(os.getenv("AGENT_TEMPERATURE", "0.7")),
            "enable_parallel_processing": os.getenv("ENABLE_PARALLEL_PROCESSING", "true").lower() == "true",
            "max_concurrent_tasks": int(os.getenv("MAX_CONCURRENT_TASKS", "3")),
        },
        "storage": {
            "pickledb_file": os.getenv("PICKLEDB_FILE", "./data/app.db"),
            "pickledb_auto_dump": os.getenv("PICKLEDB_AUTO_DUMP", "true").lower() == "true",
            "cache_enabled": os.getenv("CACHE_ENABLED", "true").lower() == "true",
            "cache_ttl": int(os.getenv("CACHE_TTL", "3600")),
            "cache_max_size": int(os.getenv("CACHE_MAX_SIZE", "1000")),
        },
        "security": {
            "rate_limit_enabled": os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true",
            "rate_limit_requests_per_minute": int(os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "60")),
            "rate_limit_requests_per_hour": int(os.getenv("RATE_LIMIT_REQUESTS_PER_HOUR", "1000")),
            "request_timeout": int(os.getenv("REQUEST_TIMEOUT", "30")),
            "connect_timeout": int(os.getenv("CONNECT_TIMEOUT", "10")),
        },
        "development": {
            "test_mode": os.getenv("TEST_MODE", "false").lower() == "true",
            "mock_external_apis": os.getenv("MOCK_EXTERNAL_APIS", "false").lower() == "true",
            "test_data_dir": os.getenv("TEST_DATA_DIR", "./tests/data"),
            "enable_profiling": os.getenv("ENABLE_PROFILING", "false").lower() == "true",
            "enable_debug_endpoints": os.getenv("ENABLE_DEBUG_ENDPOINTS", "false").lower() == "true",
        },
    }
    
    try:
        return Config(**config_data)
    except Exception as e:
        raise ValueError(f"Configuration validation failed: {e}")


# Global configuration instance
config: Optional[Config] = None


def get_config() -> Config:
    """
    Get the global configuration instance.
    
    Returns:
        Config: The global configuration instance.
        
    Raises:
        RuntimeError: If configuration has not been loaded.
    """
    if config is None:
        raise RuntimeError("Configuration not loaded. Call load_config() first.")
    return config


def initialize_config(env_file: Optional[str] = None) -> Config:
    """
    Initialize the global configuration.
    
    Args:
        env_file: Optional path to .env file.
        
    Returns:
        Config: The loaded configuration instance.
    """
    global config
    config = load_config(env_file)
    return config 