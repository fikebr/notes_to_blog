"""
Template service for loading and rendering blog post templates.

This module provides functionality for loading template files, rendering them
with data, and validating template syntax and structure.
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from jinja2 import Environment, FileSystemLoader, Template, TemplateError, TemplateSyntaxError

from src.models.blog_models import BlogPost, FrontMatter, Subheading, Image

logger = logging.getLogger(__name__)


class TemplateService:
    """Service for managing and rendering blog post templates."""
    
    def __init__(self, templates_dir: Path):
        """Initialize template service with templates directory."""
        self.templates_dir = Path(templates_dir)
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=False
        )
        self._validate_templates_directory()
    
    def _validate_templates_directory(self) -> None:
        """Validate that templates directory exists and contains required files."""
        if not self.templates_dir.exists():
            raise FileNotFoundError(f"Templates directory not found: {self.templates_dir}")
        
        required_templates = [
            "frontmatter_template.md",
            "blog_post_template.md",
            "image_prompt_templates.md"
        ]
        
        missing_templates = []
        for template_name in required_templates:
            template_path = self.templates_dir / template_name
            if not template_path.exists():
                missing_templates.append(template_name)
        
        if missing_templates:
            raise FileNotFoundError(f"Missing required templates: {', '.join(missing_templates)}")
        
        logger.info(f"Template service initialized with directory: {self.templates_dir}")
    
    def load_template(self, template_name: str) -> Template:
        """Load a template by name."""
        try:
            template = self.env.get_template(template_name)
            logger.debug(f"Loaded template: {template_name}")
            return template
        except TemplateError as e:
            logger.error(f"Failed to load template {template_name}: {e}")
            raise
    
    def render_frontmatter(self, frontmatter: FrontMatter) -> str:
        """Render frontmatter template with data."""
        try:
            template = self.load_template("frontmatter_template.md")
            
            # Prepare data for template
            template_data = {
                "title": frontmatter.title,
                "description": frontmatter.description,
                "date": frontmatter.date.strftime("%Y-%m-%d"),
                "draft": str(frontmatter.draft).lower(),
                "categories": frontmatter.categories,
                "tags": frontmatter.tags
            }
            
            rendered = template.render(**template_data)
            logger.debug(f"Rendered frontmatter for: {frontmatter.title}")
            return rendered
            
        except Exception as e:
            logger.error(f"Failed to render frontmatter: {e}")
            raise
    
    def render_blog_post(self, blog_post: BlogPost) -> str:
        """Render complete blog post template with data."""
        try:
            template = self.load_template("blog_post_template.md")
            
            # Prepare subheadings data
            subheadings_data = []
            for subheading in blog_post.subheadings:
                subheading_data = {
                    "title": subheading.title,
                    "content": subheading.content,
                    "image": None
                }
                
                # Find associated image for this subheading
                for image in blog_post.images:
                    if hasattr(image, 'subheading_order') and image.subheading_order == subheading.order:
                        subheading_data["image"] = {
                            "filename": image.filename,
                            "alt_text": image.alt_text
                        }
                        break
                
                subheadings_data.append(subheading_data)
            
            # Prepare template data
            template_data = {
                "title": blog_post.frontmatter.title,
                "description": blog_post.frontmatter.description,
                "date": blog_post.frontmatter.date.strftime("%Y-%m-%d"),
                "draft": str(blog_post.frontmatter.draft).lower(),
                "categories": blog_post.frontmatter.categories,
                "tags": blog_post.frontmatter.tags,
                "introduction": blog_post.introduction,
                "subheadings": subheadings_data,
                "conclusion": blog_post.conclusion
            }
            
            rendered = template.render(**template_data)
            logger.debug(f"Rendered blog post: {blog_post.frontmatter.title}")
            return rendered
            
        except Exception as e:
            logger.error(f"Failed to render blog post: {e}")
            raise
    
    def get_image_prompt_template(self, category: str, prompt_type: str = "header") -> str:
        """Get image prompt template for specific category and type."""
        try:
            template_content = self.load_template("image_prompt_templates.md").render()
            
            # Parse the template content to extract prompts
            prompts = self._parse_image_prompts(template_content)
            
            # Find appropriate prompt for category and type
            category_key = category.lower()
            type_key = f"{prompt_type}_image_prompts"
            
            if category_key in prompts and type_key in prompts[category_key]:
                prompt_list = prompts[category_key][type_key]
                # Return first prompt (can be enhanced to randomly select)
                return prompt_list[0] if prompt_list else self._get_default_prompt(prompt_type)
            else:
                return self._get_default_prompt(prompt_type)
                
        except Exception as e:
            logger.error(f"Failed to get image prompt template: {e}")
            return self._get_default_prompt(prompt_type)
    
    def _parse_image_prompts(self, template_content: str) -> Dict[str, Dict[str, List[str]]]:
        """Parse image prompt template content into structured data."""
        prompts = {}
        current_category = None
        current_type = None
        
        lines = template_content.split('\n')
        for line in lines:
            line = line.strip()
            
            # Parse category headers (e.g., "### Technology/Development")
            if line.startswith('### ') and not line.startswith('### Illustrative') and not line.startswith('### Supporting'):
                category_name = line[4:].split('/')[0].strip().lower()
                current_category = category_name
                prompts[current_category] = {}
            
            # Parse type headers (e.g., "## Header Image Prompts")
            elif line.startswith('## ') and 'Image Prompts' in line:
                type_name = line[3:].replace(' Image Prompts', '').lower()
                current_type = type_name
                if current_category:
                    prompts[current_category][f"{current_type}_image_prompts"] = []
            
            # Parse prompt lines
            elif line.startswith('- "') and current_category and current_type:
                prompt = line[3:-1]  # Remove '- "' and '"'
                key = f"{current_type}_image_prompts"
                if current_category in prompts and key in prompts[current_category]:
                    prompts[current_category][key].append(prompt)
        
        return prompts
    
    def _get_default_prompt(self, prompt_type: str) -> str:
        """Get default image prompt when category-specific prompt not found."""
        if prompt_type == "header":
            return "Professional blog header image, clean design, modern style, high quality photography"
        elif prompt_type == "content":
            return "Supporting visual content, professional quality, clear composition, relevant imagery"
        else:
            return "Professional image, high quality, clear composition"
    
    def validate_template_syntax(self, template_name: str) -> bool:
        """Validate template syntax without rendering."""
        try:
            template = self.load_template(template_name)
            # Try to compile the template
            template.render()
            logger.debug(f"Template syntax valid: {template_name}")
            return True
        except TemplateSyntaxError as e:
            logger.error(f"Template syntax error in {template_name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Template validation error in {template_name}: {e}")
            return False
    
    def list_available_templates(self) -> List[str]:
        """List all available templates."""
        try:
            templates = []
            for file_path in self.templates_dir.glob("*.md"):
                templates.append(file_path.name)
            return sorted(templates)
        except Exception as e:
            logger.error(f"Failed to list templates: {e}")
            return []
    
    def get_template_info(self, template_name: str) -> Dict[str, Any]:
        """Get information about a specific template."""
        try:
            template_path = self.templates_dir / template_name
            if not template_path.exists():
                raise FileNotFoundError(f"Template not found: {template_name}")
            
            template = self.load_template(template_name)
            
            return {
                "name": template_name,
                "path": str(template_path),
                "size": template_path.stat().st_size,
                "modified": datetime.fromtimestamp(template_path.stat().st_mtime),
                "variables": [],  # Jinja2 TemplateModule does not have __annotations__
                "syntax_valid": self.validate_template_syntax(template_name)
            }
            
        except Exception as e:
            logger.error(f"Failed to get template info for {template_name}: {e}")
            raise 