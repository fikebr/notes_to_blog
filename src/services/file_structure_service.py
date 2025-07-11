"""
File structure service for managing application directories and permissions.

This module provides functionality for creating and managing the application's
file structure, including inbox, output, and images directories with proper
permissions and access controls.
"""

import logging
import os
import stat
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class FileStructureService:
    """Service for managing application file structure and permissions."""
    
    def __init__(self, base_path: Path):
        """Initialize file structure service with base path."""
        self.base_path = Path(base_path)
        self.directories = {
            "inbox": self.base_path / "inbox",
            "output": self.base_path / "output", 
            "images": self.base_path / "images",
            "templates": self.base_path / "templates",
            "logs": self.base_path / "logs"
        }
        self._validate_base_path()
    
    def _validate_base_path(self) -> None:
        """Validate that base path exists and is accessible."""
        if not self.base_path.exists():
            raise FileNotFoundError(f"Base path does not exist: {self.base_path}")
        
        if not self.base_path.is_dir():
            raise NotADirectoryError(f"Base path is not a directory: {self.base_path}")
        
        if not os.access(self.base_path, os.R_OK | os.W_OK):
            raise PermissionError(f"Insufficient permissions for base path: {self.base_path}")
        
        logger.info(f"File structure service initialized with base path: {self.base_path}")
    
    def create_directory_structure(self) -> Dict[str, bool]:
        """Create all required directories."""
        results = {}
        
        for name, directory_path in self.directories.items():
            try:
                if not directory_path.exists():
                    directory_path.mkdir(parents=True, exist_ok=True)
                    logger.info(f"Created directory: {directory_path}")
                
                # Set appropriate permissions
                self._set_directory_permissions(directory_path, name)
                results[name] = True
                
            except Exception as e:
                logger.error(f"Failed to create directory {name}: {e}")
                results[name] = False
        
        return results
    
    def _set_directory_permissions(self, directory_path: Path, directory_type: str) -> None:
        """Set appropriate permissions for different directory types."""
        try:
            # Get current permissions
            current_mode = directory_path.stat().st_mode
            
            if directory_type == "inbox":
                # Inbox: Read/Write for owner, Read for group
                new_mode = current_mode | stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP
            elif directory_type == "output":
                # Output: Read/Write for owner, Read for group
                new_mode = current_mode | stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP
            elif directory_type == "images":
                # Images: Read/Write for owner, Read for group
                new_mode = current_mode | stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP
            elif directory_type == "templates":
                # Templates: Read for owner and group
                new_mode = current_mode | stat.S_IRUSR | stat.S_IRGRP
            elif directory_type == "logs":
                # Logs: Read/Write for owner, Read for group
                new_mode = current_mode | stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP
            else:
                # Default: Read/Write for owner
                new_mode = current_mode | stat.S_IRUSR | stat.S_IWUSR
            
            # Apply permissions
            directory_path.chmod(new_mode)
            logger.debug(f"Set permissions for {directory_type}: {oct(new_mode)}")
            
        except Exception as e:
            logger.warning(f"Failed to set permissions for {directory_type}: {e}")
    
    def validate_directory_structure(self) -> Dict[str, Dict[str, Any]]:
        """Validate that all required directories exist and are accessible."""
        validation_results = {}
        
        for name, directory_path in self.directories.items():
            validation = {
                "exists": False,
                "is_directory": False,
                "readable": False,
                "writable": False,
                "path": str(directory_path)
            }
            
            try:
                validation["exists"] = directory_path.exists()
                
                if validation["exists"]:
                    validation["is_directory"] = directory_path.is_dir()
                    validation["readable"] = os.access(directory_path, os.R_OK)
                    validation["writable"] = os.access(directory_path, os.W_OK)
                
                validation_results[name] = validation
                
            except Exception as e:
                logger.error(f"Error validating directory {name}: {e}")
                validation_results[name] = validation
        
        return validation_results
    
    def get_directory_info(self, directory_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific directory."""
        if directory_name not in self.directories:
            raise ValueError(f"Unknown directory: {directory_name}")
        
        directory_path = self.directories[directory_name]
        
        try:
            if not directory_path.exists():
                return {
                    "name": directory_name,
                    "path": str(directory_path),
                    "exists": False,
                    "error": "Directory does not exist"
                }
            
            stat_info = directory_path.stat()
            
            # Count files in directory
            file_count = 0
            total_size = 0
            
            try:
                for item in directory_path.iterdir():
                    if item.is_file():
                        file_count += 1
                        total_size += item.stat().st_size
            except PermissionError:
                logger.warning(f"No permission to read directory contents: {directory_path}")
            
            return {
                "name": directory_name,
                "path": str(directory_path),
                "exists": True,
                "is_directory": directory_path.is_dir(),
                "readable": os.access(directory_path, os.R_OK),
                "writable": os.access(directory_path, os.W_OK),
                "created": datetime.fromtimestamp(stat_info.st_ctime),
                "modified": datetime.fromtimestamp(stat_info.st_mtime),
                "file_count": file_count,
                "total_size": total_size,
                "permissions": oct(stat_info.st_mode)[-3:]
            }
            
        except Exception as e:
            logger.error(f"Error getting directory info for {directory_name}: {e}")
            return {
                "name": directory_name,
                "path": str(directory_path),
                "exists": False,
                "error": str(e)
            }
    
    def list_directory_contents(self, directory_name: str) -> List[Dict[str, Any]]:
        """List contents of a specific directory."""
        if directory_name not in self.directories:
            raise ValueError(f"Unknown directory: {directory_name}")
        
        directory_path = self.directories[directory_name]
        contents = []
        
        try:
            if not directory_path.exists():
                logger.warning(f"Directory does not exist: {directory_path}")
                return contents
            
            for item in directory_path.iterdir():
                try:
                    stat_info = item.stat()
                    content_info = {
                        "name": item.name,
                        "path": str(item),
                        "is_file": item.is_file(),
                        "is_directory": item.is_dir(),
                        "size": stat_info.st_size if item.is_file() else 0,
                        "created": datetime.fromtimestamp(stat_info.st_ctime),
                        "modified": datetime.fromtimestamp(stat_info.st_mtime),
                        "permissions": oct(stat_info.st_mode)[-3:]
                    }
                    contents.append(content_info)
                    
                except PermissionError:
                    logger.warning(f"No permission to access: {item}")
                except Exception as e:
                    logger.warning(f"Error accessing {item}: {e}")
            
            # Sort by name
            contents.sort(key=lambda x: x["name"])
            
        except Exception as e:
            logger.error(f"Error listing directory contents for {directory_name}: {e}")
        
        return contents
    
    def cleanup_directory(self, directory_name: str, max_age_days: int = 30) -> Dict[str, Any]:
        """Clean up old files in a directory based on age."""
        if directory_name not in self.directories:
            raise ValueError(f"Unknown directory: {directory_name}")
        
        directory_path = self.directories[directory_name]
        cleanup_results = {
            "directory": directory_name,
            "files_checked": 0,
            "files_removed": 0,
            "errors": 0,
            "removed_files": []
        }
        
        try:
            if not directory_path.exists():
                logger.warning(f"Directory does not exist: {directory_path}")
                return cleanup_results
            
            cutoff_time = datetime.now().timestamp() - (max_age_days * 24 * 60 * 60)
            
            for item in directory_path.iterdir():
                if item.is_file():
                    cleanup_results["files_checked"] += 1
                    
                    try:
                        file_age = item.stat().st_mtime
                        
                        if file_age < cutoff_time:
                            item.unlink()
                            cleanup_results["files_removed"] += 1
                            cleanup_results["removed_files"].append(item.name)
                            logger.info(f"Removed old file: {item}")
                            
                    except PermissionError:
                        logger.warning(f"No permission to remove: {item}")
                        cleanup_results["errors"] += 1
                    except Exception as e:
                        logger.error(f"Error removing {item}: {e}")
                        cleanup_results["errors"] += 1
            
        except Exception as e:
            logger.error(f"Error during cleanup of {directory_name}: {e}")
            cleanup_results["errors"] += 1
        
        return cleanup_results
    
    def get_storage_usage(self) -> Dict[str, Any]:
        """Get storage usage information for all directories."""
        usage_info = {
            "total_size": 0,
            "directory_usage": {},
            "total_files": 0
        }
        
        for name, directory_path in self.directories.items():
            try:
                if directory_path.exists():
                    size = 0
                    file_count = 0
                    
                    for item in directory_path.rglob("*"):
                        if item.is_file():
                            size += item.stat().st_size
                            file_count += 1
                    
                    usage_info["directory_usage"][name] = {
                        "size": size,
                        "file_count": file_count,
                        "path": str(directory_path)
                    }
                    
                    usage_info["total_size"] += size
                    usage_info["total_files"] += file_count
                else:
                    usage_info["directory_usage"][name] = {
                        "size": 0,
                        "file_count": 0,
                        "path": str(directory_path),
                        "exists": False
                    }
                    
            except Exception as e:
                logger.error(f"Error calculating usage for {name}: {e}")
                usage_info["directory_usage"][name] = {
                    "size": 0,
                    "file_count": 0,
                    "path": str(directory_path),
                    "error": str(e)
                }
        
        return usage_info 