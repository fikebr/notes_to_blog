"""
Logging configuration and utilities for the Notes to Blog application.

This module provides comprehensive logging setup with file rotation,
dual output (console and file), and utility functions for logging.
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

# from config import get_config  # Removed for testing


def setup_logging(
    log_file_path: Optional[Path] = None,
    console_level: int = logging.INFO,
    file_level: int = logging.DEBUG,
    log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    max_bytes: int = 10_485_760,  # 10 MB
    backup_count: int = 3,
    encoding: str = 'utf-8'
) -> logging.Logger:
    """
    Set up comprehensive logging with file rotation and dual output.
    
    Args:
        log_file_path: Path to log file. If None, uses default.
        console_level: Logging level for console output.
        file_level: Logging level for file output.
        log_format: Format string for log messages.
        max_bytes: Maximum size of log file before rotation.
        backup_count: Number of backup files to keep.
        encoding: File encoding for log files.
        
    Returns:
        logging.Logger: Configured logger instance.
    """
    # Use default log file path if none provided
    if log_file_path is None:
        log_file_path = Path("./logs/app.log")
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Set to lowest level, handlers will filter
    
    # Clear existing handlers to avoid duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Ensure log directory exists
    log_dir = log_file_path.parent
    if log_dir and not log_dir.exists():
        log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create file handler with rotation
    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding=encoding
    )
    
    file_handler.setLevel(file_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Log initialization completion
    logger.info(f"Logging initialized: console={logging.getLevelName(console_level)}, "
                f"file={logging.getLevelName(file_level)} at '{log_file_path}'")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (usually __name__).
        
    Returns:
        logging.Logger: Logger instance.
    """
    return logging.getLogger(name)


def configure_logging_from_config() -> logging.Logger:
    """
    Configure logging using application configuration.
    
    Returns:
        logging.Logger: Configured logger instance.
    """
    # For now, use default configuration
    return setup_logging()


def log_function_entry(logger: logging.Logger, function_name: str, **kwargs) -> None:
    """
    Log function entry with parameters.
    
    Args:
        logger: Logger instance to use.
        function_name: Name of the function being entered.
        **kwargs: Function parameters to log.
    """
    params_str = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
    logger.debug(f"Entering {function_name}({params_str})")


def log_function_exit(logger: logging.Logger, function_name: str, result: Optional[object] = None) -> None:
    """
    Log function exit with optional result.
    
    Args:
        logger: Logger instance to use.
        function_name: Name of the function being exited.
        result: Optional result to log.
    """
    if result is not None:
        logger.debug(f"Exiting {function_name} -> {result}")
    else:
        logger.debug(f"Exiting {function_name}")


def log_error(logger: logging.Logger, error: Exception, function_name: str, line_number: Optional[int] = None) -> None:
    """
    Log error with context information.
    
    Args:
        logger: Logger instance to use.
        error: Exception that occurred.
        function_name: Name of the function where error occurred.
        line_number: Optional line number where error occurred.
    """
    context = f" in {function_name}"
    if line_number:
        context += f" at line {line_number}"
    
    logger.error(f"Error{context}: {error}", exc_info=True)


def log_performance(logger: logging.Logger, operation: str, duration: float, **context) -> None:
    """
    Log performance metrics.
    
    Args:
        logger: Logger instance to use.
        operation: Name of the operation being measured.
        duration: Duration in seconds.
        **context: Additional context information.
    """
    context_str = ", ".join([f"{k}={v}" for k, v in context.items()])
    logger.info(f"Performance: {operation} took {duration:.3f}s {context_str}")


# Global logger instance
_logger: Optional[logging.Logger] = None


def initialize_logging() -> logging.Logger:
    """
    Initialize global logging instance.
    
    Returns:
        logging.Logger: Global logger instance.
    """
    global _logger
    if _logger is None:
        _logger = setup_logging()
    return _logger


def get_global_logger() -> logging.Logger:
    """
    Get the global logger instance.
    
    Returns:
        logging.Logger: Global logger instance.
    """
    if _logger is None:
        return initialize_logging()
    return _logger 