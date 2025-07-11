"""
Input Processor Service for monitoring and processing note files.

This service handles inbox monitoring, file validation, format detection,
and parsing of various input formats for the blog post creation workflow.
"""

import logging
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Generator
from datetime import datetime
import mimetypes

from src.models.config_models import Config
from src.models.blog_models import Note

logger = logging.getLogger(__name__)


class InputProcessor:
    """Service for processing input notes from the inbox directory."""
    
    SUPPORTED_EXTENSIONS = ['.txt', '.md', '.markdown', '.rtf', '.docx']
    SUPPORTED_MIME_TYPES = [
        'text/plain',
        'text/markdown',
        'text/x-markdown',
        'application/rtf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ]
    
    def __init__(self, config: Config):
        """Initialize the input processor."""
        self.config = config
        self.inbox_path = Path(config.paths.inbox_dir)
        
        # Ensure inbox directory exists
        self.inbox_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Input processor initialized with inbox: {self.inbox_path}")
    
    def monitor_inbox(self) -> Generator[Note, None, None]:
        """Monitor inbox directory for new note files."""
        try:
            logger.info("Starting inbox monitoring")
            
            for file_path in self.inbox_path.iterdir():
                if file_path.is_file() and self._is_supported_file(file_path):
                    try:
                        note = self._process_file(file_path)
                        if note:
                            yield note
                    except Exception as e:
                        logger.error(f"Failed to process file {file_path}: {e}")
                        continue
            
            logger.info("Inbox monitoring completed")
            
        except Exception as e:
            logger.error(f"Inbox monitoring failed: {e}")
            raise
    
    def process_single_file(self, file_path: str) -> Optional[Note]:
        """Process a single note file."""
        try:
            path = Path(file_path)
            if not path.exists():
                logger.error(f"File not found: {file_path}")
                return None
            
            if not self._is_supported_file(path):
                logger.error(f"Unsupported file type: {file_path}")
                return None
            
            return self._process_file(path)
            
        except Exception as e:
            logger.error(f"Failed to process single file {file_path}: {e}")
            return None
    
    def validate_note_file(self, file_path: Path) -> Dict[str, Any]:
        """Validate a note file for processing."""
        try:
            validation_result = {
                "is_valid": False,
                "file_path": str(file_path),
                "file_size": 0,
                "file_type": "unknown",
                "encoding": "unknown",
                "errors": []
            }
            
            # Check if file exists
            if not file_path.exists():
                validation_result["errors"].append("File does not exist")
                return validation_result
            
            # Check file size
            file_size = file_path.stat().st_size
            validation_result["file_size"] = file_size
            
            if file_size == 0:
                validation_result["errors"].append("File is empty")
                return validation_result
            
            if file_size > 10 * 1024 * 1024:  # 10MB limit
                validation_result["errors"].append("File too large (max 10MB)")
                return validation_result
            
            # Check file extension
            file_extension = file_path.suffix.lower()
            if file_extension not in self.SUPPORTED_EXTENSIONS:
                validation_result["errors"].append(f"Unsupported file extension: {file_extension}")
                return validation_result
            
            validation_result["file_type"] = file_extension
            
            # Check MIME type
            mime_type, _ = mimetypes.guess_type(str(file_path))
            if mime_type and mime_type not in self.SUPPORTED_MIME_TYPES:
                validation_result["errors"].append(f"Unsupported MIME type: {mime_type}")
                return validation_result
            
            # Check if file is readable
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    f.read(1024)  # Read first 1KB to test encoding
                validation_result["encoding"] = "utf-8"
            except UnicodeDecodeError:
                try:
                    with open(file_path, 'r', encoding='latin-1') as f:
                        f.read(1024)
                    validation_result["encoding"] = "latin-1"
                except Exception as e:
                    validation_result["errors"].append(f"File encoding error: {e}")
                    return validation_result
            except Exception as e:
                validation_result["errors"].append(f"File read error: {e}")
                return validation_result
            
            # If we get here, file is valid
            validation_result["is_valid"] = True
            logger.info(f"File validation successful: {file_path}")
            return validation_result
            
        except Exception as e:
            logger.error(f"File validation failed for {file_path}: {e}")
            validation_result["errors"].append(f"Validation error: {e}")
            return validation_result
    
    def _is_supported_file(self, file_path: Path) -> bool:
        """Check if file is supported for processing."""
        try:
            # Check extension
            if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                return False
            
            # Check if it's a regular file
            if not file_path.is_file():
                return False
            
            # Check if it's not a hidden file
            if file_path.name.startswith('.'):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking file support for {file_path}: {e}")
            return False
    
    def _process_file(self, file_path: Path) -> Optional[Note]:
        """Process a single file and create a Note object."""
        try:
            # Validate file first
            validation = self.validate_note_file(file_path)
            if not validation["is_valid"]:
                logger.error(f"File validation failed: {validation['errors']}")
                return None
            
            # Read file content
            content = self._read_file_content(file_path, validation["encoding"])
            if not content:
                logger.error(f"Failed to read content from {file_path}")
                return None
            
            # Create Note object
            note = Note(
                content=content,
                filename=file_path.name,
                created_at=datetime.fromtimestamp(file_path.stat().st_ctime),
                source="inbox",
                file_path=str(file_path),
                file_size=validation["file_size"],
                file_type=validation["file_type"]
            )
            
            logger.info(f"Successfully processed file: {file_path.name}")
            return note
            
        except Exception as e:
            logger.error(f"Failed to process file {file_path}: {e}")
            return None
    
    def _read_file_content(self, file_path: Path, encoding: str) -> Optional[str]:
        """Read content from file with specified encoding."""
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            # Basic content validation
            if not content.strip():
                logger.warning(f"File {file_path} contains only whitespace")
                return None
            
            # Remove BOM if present
            if content.startswith('\ufeff'):
                content = content[1:]
            
            return content.strip()
            
        except Exception as e:
            logger.error(f"Failed to read file content from {file_path}: {e}")
            return None
    
    def get_inbox_status(self) -> Dict[str, Any]:
        """Get status of the inbox directory."""
        try:
            total_files = 0
            supported_files = 0
            processed_files = 0
            error_files = 0
            
            for file_path in self.inbox_path.iterdir():
                if file_path.is_file():
                    total_files += 1
                    
                    if self._is_supported_file(file_path):
                        supported_files += 1
                        
                        # Try to process the file
                        try:
                            note = self._process_file(file_path)
                            if note:
                                processed_files += 1
                            else:
                                error_files += 1
                        except Exception:
                            error_files += 1
                    else:
                        error_files += 1
            
            return {
                "inbox_path": str(self.inbox_path),
                "total_files": total_files,
                "supported_files": supported_files,
                "processed_files": processed_files,
                "error_files": error_files,
                "supported_extensions": self.SUPPORTED_EXTENSIONS,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get inbox status: {e}")
            return {
                "inbox_path": str(self.inbox_path),
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def cleanup_processed_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """Clean up processed files from inbox."""
        try:
            results = {
                "successful": [],
                "failed": [],
                "not_found": []
            }
            
            for file_path_str in file_paths:
                file_path = Path(file_path_str)
                
                if not file_path.exists():
                    results["not_found"].append(file_path_str)
                    continue
                
                try:
                    # Move to processed directory or delete
                    processed_dir = self.inbox_path / "processed"
                    processed_dir.mkdir(exist_ok=True)
                    
                    new_path = processed_dir / file_path.name
                    file_path.rename(new_path)
                    results["successful"].append(file_path_str)
                    
                    logger.info(f"Moved processed file: {file_path.name}")
                    
                except Exception as e:
                    logger.error(f"Failed to cleanup file {file_path_str}: {e}")
                    results["failed"].append(file_path_str)
            
            return results
            
        except Exception as e:
            logger.error(f"Cleanup operation failed: {e}")
            return {
                "successful": [],
                "failed": file_paths,
                "not_found": [],
                "error": str(e)
            } 