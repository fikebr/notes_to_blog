"""
Output Generator Service for creating final blog post files.

This service handles markdown file generation, frontmatter insertion,
image file management, and output validation for the blog post creation workflow.
"""

import logging
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.models.config_models import Config
from src.models.blog_models import BlogPost, FrontMatter, Image

logger = logging.getLogger(__name__)


class OutputGenerator:
    """Service for generating final blog post output files."""
    
    def __init__(self, config: Config):
        """Initialize the output generator."""
        self.config = config
        self.output_path = Path(config.paths.output_dir)
        self.images_path = Path(config.paths.images_dir)
        
        # Ensure output directories exist
        self.output_path.mkdir(parents=True, exist_ok=True)
        self.images_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Output generator initialized with output: {self.output_path}")
    
    def generate_blog_post_file(self, blog_post: BlogPost) -> Dict[str, Any]:
        """Generate the final blog post markdown file."""
        try:
            logger.info(f"Generating blog post file: {blog_post.filename}")
            
            # Validate blog post
            validation_result = self._validate_blog_post(blog_post)
            if not validation_result["is_valid"]:
                logger.error(f"Blog post validation failed: {validation_result['errors']}")
                return {
                    "success": False,
                    "errors": validation_result["errors"],
                    "file_path": None
                }
            
            # Generate frontmatter
            frontmatter_content = self._generate_frontmatter_content(blog_post.frontmatter)
            
            # Combine frontmatter and content
            full_content = f"{frontmatter_content}\n\n{blog_post.content}"
            
            # Determine output file path
            output_file_path = self._get_output_file_path(blog_post.filename)
            
            # Write the file
            with open(output_file_path, 'w', encoding='utf-8') as f:
                f.write(full_content)
            
            # Copy images to output directory if needed
            image_results = self._manage_images(blog_post.images, output_file_path)
            
            # Generate final result
            result = {
                "success": True,
                "file_path": str(output_file_path),
                "file_size": output_file_path.stat().st_size,
                "content_length": len(full_content),
                "images": image_results,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Blog post file generated successfully: {output_file_path}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate blog post file: {e}")
            return {
                "success": False,
                "errors": [str(e)],
                "file_path": None
            }
    
    def _validate_blog_post(self, blog_post: BlogPost) -> Dict[str, Any]:
        """Validate blog post before generation."""
        try:
            validation_result = {
                "is_valid": False,
                "errors": []
            }
            
            # Check required fields
            if not blog_post.frontmatter.title:
                validation_result["errors"].append("Missing title in frontmatter")
            
            if not blog_post.frontmatter.description:
                validation_result["errors"].append("Missing description in frontmatter")
            
            if not blog_post.content:
                validation_result["errors"].append("Missing content")
            
            if not blog_post.filename:
                validation_result["errors"].append("Missing filename")
            
            # Check content length
            if len(blog_post.content) < 100:
                validation_result["errors"].append("Content too short (minimum 100 characters)")
            
            if len(blog_post.content) > 50000:
                validation_result["errors"].append("Content too long (maximum 50,000 characters)")
            
            # Check filename format
            if not blog_post.filename.endswith('.md'):
                validation_result["errors"].append("Filename must end with .md")
            
            # Check for invalid characters in filename
            invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
            if any(char in blog_post.filename for char in invalid_chars):
                validation_result["errors"].append("Filename contains invalid characters")
            
            # If no errors, mark as valid
            if not validation_result["errors"]:
                validation_result["is_valid"] = True
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Blog post validation failed: {e}")
            return {
                "is_valid": False,
                "errors": [f"Validation error: {e}"]
            }
    
    def _generate_frontmatter_content(self, frontmatter: FrontMatter) -> str:
        """Generate frontmatter content in TOML format."""
        try:
            frontmatter_lines = [
                "+++",
                f'title = "{self._escape_toml_string(frontmatter.title)}"',
                f'description = "{self._escape_toml_string(frontmatter.description)}"',
                f'date = "{frontmatter.date}"',
                f'draft = {str(frontmatter.draft).lower()}',
                "",
                "[taxonomies]",
                f'categories = {self._format_toml_array(frontmatter.categories)}',
                f'tags = {self._format_toml_array(frontmatter.tags)}',
                "+++"
            ]
            
            return "\n".join(frontmatter_lines)
            
        except Exception as e:
            logger.error(f"Failed to generate frontmatter content: {e}")
            # Return minimal frontmatter as fallback
            return f"""+++
title = "{frontmatter.title or 'Blog Post'}"
description = "{frontmatter.description or 'Blog post description'}"
date = "{frontmatter.date or datetime.now().strftime('%Y-%m-%d')}"
draft = true

[taxonomies]
categories = ["development"]
tags = ["blog"]
+++"""
    
    def _escape_toml_string(self, text: str) -> str:
        """Escape special characters in TOML strings."""
        try:
            # Replace backslashes and quotes
            escaped = text.replace('\\', '\\\\').replace('"', '\\"')
            return escaped
        except Exception:
            return text
    
    def _format_toml_array(self, items: List[str]) -> str:
        """Format a list as a TOML array."""
        try:
            if not items:
                return '[]'
            
            formatted_items = [f'"{self._escape_toml_string(item)}"' for item in items]
            return f'[{", ".join(formatted_items)}]'
            
        except Exception as e:
            logger.error(f"Failed to format TOML array: {e}")
            return '["blog"]'
    
    def _get_output_file_path(self, filename: str) -> Path:
        """Get the output file path for the blog post."""
        try:
            # Ensure filename has .md extension
            if not filename.endswith('.md'):
                filename = f"{filename}.md"
            
            # Create output path
            output_file_path = self.output_path / filename
            
            # Handle filename conflicts
            counter = 1
            original_path = output_file_path
            while output_file_path.exists():
                name_without_ext = original_path.stem
                output_file_path = self.output_path / f"{name_without_ext}_{counter}.md"
                counter += 1
            
            return output_file_path
            
        except Exception as e:
            logger.error(f"Failed to get output file path: {e}")
            # Fallback to timestamp-based filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return self.output_path / f"blog_post_{timestamp}.md"
    
    def _manage_images(self, images: List[Image], blog_post_path: Path) -> Dict[str, Any]:
        """Manage image files for the blog post."""
        try:
            image_results = {
                "copied": [],
                "failed": [],
                "not_found": []
            }
            
            if not images:
                return image_results
            
            # Create images subdirectory for this blog post
            blog_post_name = blog_post_path.stem
            blog_post_images_dir = self.images_path / blog_post_name
            blog_post_images_dir.mkdir(exist_ok=True)
            
            for image in images:
                try:
                    source_path = Path(image.path)
                    
                    if not source_path.exists():
                        image_results["not_found"].append(image.path)
                        continue
                    
                    # Copy image to blog post images directory
                    dest_path = blog_post_images_dir / source_path.name
                    shutil.copy2(source_path, dest_path)
                    
                    # Update image path to relative path
                    relative_path = f"images/{blog_post_name}/{source_path.name}"
                    image.path = relative_path
                    
                    image_results["copied"].append({
                        "original_path": image.path,
                        "new_path": relative_path,
                        "alt_text": image.alt_text
                    })
                    
                    logger.info(f"Copied image: {source_path.name}")
                    
                except Exception as e:
                    logger.error(f"Failed to copy image {image.path}: {e}")
                    image_results["failed"].append({
                        "path": image.path,
                        "error": str(e)
                    })
            
            return image_results
            
        except Exception as e:
            logger.error(f"Image management failed: {e}")
            return {
                "copied": [],
                "failed": [],
                "not_found": [],
                "error": str(e)
            }
    
    def validate_output_file(self, file_path: Path) -> Dict[str, Any]:
        """Validate a generated output file."""
        try:
            validation_result = {
                "is_valid": False,
                "file_path": str(file_path),
                "file_size": 0,
                "has_frontmatter": False,
                "has_content": False,
                "errors": []
            }
            
            if not file_path.exists():
                validation_result["errors"].append("File does not exist")
                return validation_result
            
            # Check file size
            file_size = file_path.stat().st_size
            validation_result["file_size"] = file_size
            
            if file_size == 0:
                validation_result["errors"].append("File is empty")
                return validation_result
            
            # Read and validate content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for frontmatter
            if "+++" in content:
                validation_result["has_frontmatter"] = True
            else:
                validation_result["errors"].append("Missing frontmatter")
            
            # Check for content after frontmatter
            if len(content.strip()) > 100:
                validation_result["has_content"] = True
            else:
                validation_result["errors"].append("Insufficient content")
            
            # Check for required frontmatter fields
            if "title =" in content and "description =" in content:
                pass  # Basic frontmatter fields present
            else:
                validation_result["errors"].append("Missing required frontmatter fields")
            
            # If no errors, mark as valid
            if not validation_result["errors"]:
                validation_result["is_valid"] = True
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Output file validation failed: {e}")
            return {
                "is_valid": False,
                "file_path": str(file_path),
                "errors": [f"Validation error: {e}"]
            }
    
    def get_output_status(self) -> Dict[str, Any]:
        """Get status of the output directory."""
        try:
            total_files = 0
            valid_files = 0
            invalid_files = 0
            total_size = 0
            
            for file_path in self.output_path.iterdir():
                if file_path.is_file() and file_path.suffix == '.md':
                    total_files += 1
                    total_size += file_path.stat().st_size
                    
                    validation = self.validate_output_file(file_path)
                    if validation["is_valid"]:
                        valid_files += 1
                    else:
                        invalid_files += 1
            
            return {
                "output_path": str(self.output_path),
                "total_files": total_files,
                "valid_files": valid_files,
                "invalid_files": invalid_files,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get output status: {e}")
            return {
                "output_path": str(self.output_path),
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def cleanup_old_files(self, days_old: int = 30) -> Dict[str, Any]:
        """Clean up old output files."""
        try:
            cutoff_date = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
            
            results = {
                "deleted": [],
                "failed": [],
                "total_size_freed": 0
            }
            
            for file_path in self.output_path.iterdir():
                if file_path.is_file() and file_path.suffix == '.md':
                    file_age = file_path.stat().st_mtime
                    
                    if file_age < cutoff_date:
                        try:
                            file_size = file_path.stat().st_size
                            file_path.unlink()
                            results["deleted"].append(str(file_path))
                            results["total_size_freed"] += file_size
                            
                            logger.info(f"Deleted old file: {file_path.name}")
                            
                        except Exception as e:
                            logger.error(f"Failed to delete old file {file_path}: {e}")
                            results["failed"].append(str(file_path))
            
            results["total_size_freed_mb"] = round(results["total_size_freed"] / (1024 * 1024), 2)
            return results
            
        except Exception as e:
            logger.error(f"Cleanup operation failed: {e}")
            return {
                "deleted": [],
                "failed": [],
                "total_size_freed": 0,
                "error": str(e)
            } 