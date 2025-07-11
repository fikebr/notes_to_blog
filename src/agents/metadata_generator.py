"""
Metadata Generator Agent for creating SEO-optimized blog post metadata.

This agent is responsible for selecting categories, generating tags, creating
frontmatter, and generating appropriate filenames for blog posts.
"""

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from src.agents.base_agent import BaseAgent, AgentConfig

logger = logging.getLogger(__name__)


class MetadataGeneratorAgent(BaseAgent):
    """Agent for generating blog post metadata and frontmatter."""
    
    # Predefined categories from PRD
    AVAILABLE_CATEGORIES = [
        "development", "computer", "home", "ai", "business", 
        "crafting", "health", "diy", "recipes"
    ]
    
    def _get_agent_config(self) -> AgentConfig:
        """Get metadata generator agent configuration."""
        return AgentConfig(
            name="Metadata Generator",
            role="Metadata Generation Specialist",
            goal="Create SEO-optimized metadata including categories, tags, frontmatter, and filenames for blog posts",
            backstory="""You are an expert in SEO and content metadata with deep 
            understanding of how proper categorization, tagging, and frontmatter 
            can significantly impact a blog post's discoverability and search 
            engine performance. You excel at creating metadata that enhances 
            both user experience and SEO value.""",
            verbose=self.config.crewai.agent_verbose,
            allow_delegation=False,
            max_iterations=self.config.crewai.agent_max_iterations,
            memory=self.config.crewai.agent_memory
        )
    
    def _get_prompt_template_path(self) -> Path:
        """Get path to metadata generator prompt template."""
        return Path("templates/agent_prompts/metadata_generator.txt")
    
    def _get_default_prompt_template(self) -> str:
        """Get default prompt template for metadata generator."""
        return """You are a Metadata Generation Specialist with expertise in creating SEO-optimized metadata for blog posts.

TASK: {task_description}

Your responsibilities:
1. Select the most appropriate category from predefined options
2. Generate 2-5 relevant, SEO-friendly tags
3. Create comprehensive frontmatter metadata
4. Generate appropriate filenames for blog posts
5. Ensure metadata enhances discoverability and SEO

Please provide metadata in a structured JSON format with category, tags, filename, and frontmatter."""
    
    def generate_metadata(self, title: str, description: str, content: str) -> Dict[str, Any]:
        """Generate comprehensive metadata for a blog post."""
        try:
            task_description = f"""
            Generate comprehensive metadata for this blog post:
            
            TITLE: {title}
            DESCRIPTION: {description}
            CONTENT PREVIEW: {content[:500]}...
            
            Please provide complete metadata including category, tags, filename, and frontmatter.
            """
            
            result = self.execute_task(task_description)
            
            # Try to parse JSON response
            try:
                metadata = json.loads(result)
                logger.info("Generated comprehensive metadata")
                return metadata
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON response, generating fallback metadata")
                return self._generate_fallback_metadata(title, description)
                
        except Exception as e:
            logger.error(f"Failed to generate metadata: {e}")
            return self._generate_fallback_metadata(title, description)
    
    def select_category(self, title: str, content: str) -> str:
        """Select the most appropriate category for the blog post."""
        try:
            task_description = f"""
            Select the most appropriate category for this blog post from the available options:
            
            TITLE: {title}
            CONTENT PREVIEW: {content[:300]}...
            
            AVAILABLE CATEGORIES: {', '.join(self.AVAILABLE_CATEGORIES)}
            
            Choose the category that best represents the main topic and content of this post.
            Return only the category name.
            """
            
            result = self.execute_task(task_description)
            selected_category = result.strip().lower()
            
            # Validate the selected category
            if selected_category in self.AVAILABLE_CATEGORIES:
                logger.info(f"Selected category: {selected_category}")
                return selected_category
            else:
                logger.warning(f"Invalid category '{selected_category}', using default")
                return self._determine_default_category(title, content)
                
        except Exception as e:
            logger.error(f"Failed to select category: {e}")
            return self._determine_default_category(title, content)
    
    def generate_tags(self, title: str, content: str, category: str) -> List[str]:
        """Generate 2-5 relevant, SEO-friendly tags."""
        try:
            task_description = f"""
            Generate 2-5 relevant, SEO-friendly tags for this blog post:
            
            TITLE: {title}
            CONTENT PREVIEW: {content[:300]}...
            CATEGORY: {category}
            
            The tags should:
            - Be specific and relevant to the content
            - Complement the category
            - Be searchable and SEO-friendly
            - Avoid overly generic terms
            - Be limited to 2-5 tags for optimal focus
            
            Return the tags as a simple list, one per line.
            """
            
            result = self.execute_task(task_description)
            
            # Extract tags from response
            tags = self._extract_tags(result)
            
            # Ensure we have 2-5 tags
            if len(tags) < 2:
                tags.extend(self._generate_fallback_tags(category))
            elif len(tags) > 5:
                tags = tags[:5]
            
            logger.info(f"Generated tags: {tags}")
            return tags
            
        except Exception as e:
            logger.error(f"Failed to generate tags: {e}")
            return self._generate_fallback_tags(category)
    
    def generate_filename(self, title: str, category: str) -> str:
        """Generate an SEO-friendly filename for the blog post."""
        try:
            task_description = f"""
            Generate an SEO-friendly filename for this blog post:
            
            TITLE: {title}
            CATEGORY: {category}
            
            The filename should:
            - Be descriptive and SEO-friendly
            - Use lowercase letters and hyphens
            - Include relevant keywords
            - Be concise but descriptive
            - End with .md extension
            
            Return only the filename (e.g., "seo-friendly-blog-post-title.md").
            """
            
            result = self.execute_task(task_description)
            filename = result.strip()
            
            # Clean up the filename
            filename = self._clean_filename(filename)
            
            logger.info(f"Generated filename: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Failed to generate filename: {e}")
            return self._generate_fallback_filename(title)
    
    def create_frontmatter(self, title: str, description: str, category: str, tags: List[str]) -> Dict[str, Any]:
        """Create comprehensive frontmatter for the blog post."""
        try:
            task_description = f"""
            Create comprehensive frontmatter for this blog post:
            
            TITLE: {title}
            DESCRIPTION: {description}
            CATEGORY: {category}
            TAGS: {', '.join(tags)}
            
            The frontmatter should include:
            - title
            - description
            - date (current date)
            - draft status (true)
            - taxonomies (categories and tags)
            
            Return the frontmatter in JSON format.
            """
            
            result = self.execute_task(task_description)
            
            try:
                frontmatter = json.loads(result)
                logger.info("Generated frontmatter")
                return frontmatter
            except json.JSONDecodeError:
                logger.warning("Failed to parse frontmatter JSON, using fallback")
                return self._generate_fallback_frontmatter(title, description, category, tags)
                
        except Exception as e:
            logger.error(f"Failed to create frontmatter: {e}")
            return self._generate_fallback_frontmatter(title, description, category, tags)
    
    def _extract_tags(self, response: str) -> List[str]:
        """Extract tags from the response."""
        try:
            tags = []
            lines = response.split('\n')
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#') and len(line) > 2:
                    # Remove common prefixes
                    for prefix in ['- ', '* ', '1. ', '2. ', '3. ', '4. ', '5. ']:
                        if line.startswith(prefix):
                            line = line[len(prefix):]
                            break
                    
                    # Clean up the tag
                    tag = line.lower().strip()
                    if tag and len(tag) > 1:
                        tags.append(tag)
            
            return tags
        except Exception as e:
            logger.error(f"Failed to extract tags: {e}")
            return []
    
    def _clean_filename(self, filename: str) -> str:
        """Clean and format the filename."""
        try:
            # Remove .md extension if present
            if filename.endswith('.md'):
                filename = filename[:-3]
            
            # Convert to lowercase
            filename = filename.lower()
            
            # Replace spaces and special characters with hyphens
            filename = re.sub(r'[^a-z0-9\s-]', '', filename)
            filename = re.sub(r'[\s-]+', '-', filename)
            
            # Remove leading/trailing hyphens
            filename = filename.strip('-')
            
            # Add .md extension
            filename = f"{filename}.md"
            
            return filename
        except Exception as e:
            logger.error(f"Failed to clean filename: {e}")
            return "blog-post.md"
    
    def _determine_default_category(self, title: str, content: str) -> str:
        """Determine default category based on content analysis."""
        try:
            # Simple keyword-based category selection
            text = f"{title} {content}".lower()
            
            if any(word in text for word in ["code", "programming", "software", "development"]):
                return "development"
            elif any(word in text for word in ["computer", "tech", "technology"]):
                return "computer"
            elif any(word in text for word in ["ai", "artificial intelligence", "machine learning"]):
                return "ai"
            elif any(word in text for word in ["business", "marketing", "entrepreneur"]):
                return "business"
            elif any(word in text for word in ["health", "fitness", "wellness"]):
                return "health"
            elif any(word in text for word in ["craft", "art", "creative"]):
                return "crafting"
            elif any(word in text for word in ["diy", "do it yourself", "project"]):
                return "diy"
            elif any(word in text for word in ["recipe", "cooking", "food"]):
                return "recipes"
            elif any(word in text for word in ["home", "house", "garden"]):
                return "home"
            else:
                return "development"  # Default fallback
                
        except Exception as e:
            logger.error(f"Failed to determine default category: {e}")
            return "development"
    
    def _generate_fallback_tags(self, category: str) -> List[str]:
        """Generate fallback tags based on category."""
        try:
            tag_mapping = {
                "development": ["programming", "coding", "software"],
                "computer": ["technology", "tech", "computing"],
                "home": ["household", "lifestyle", "home-improvement"],
                "ai": ["artificial-intelligence", "machine-learning", "automation"],
                "business": ["entrepreneurship", "marketing", "strategy"],
                "crafting": ["art", "creative", "handmade"],
                "health": ["wellness", "fitness", "lifestyle"],
                "diy": ["projects", "how-to", "tutorial"],
                "recipes": ["cooking", "food", "kitchen"]
            }
            
            return tag_mapping.get(category, ["blog", "article"])
            
        except Exception as e:
            logger.error(f"Failed to generate fallback tags: {e}")
            return ["blog", "article"]
    
    def _generate_fallback_filename(self, title: str) -> str:
        """Generate fallback filename from title."""
        try:
            return self._clean_filename(title)
        except Exception as e:
            logger.error(f"Failed to generate fallback filename: {e}")
            return "blog-post.md"
    
    def _generate_fallback_metadata(self, title: str, description: str) -> Dict[str, Any]:
        """Generate fallback metadata when primary generation fails."""
        try:
            category = self._determine_default_category(title, "")
            tags = self._generate_fallback_tags(category)
            filename = self._generate_fallback_filename(title)
            frontmatter = self._generate_fallback_frontmatter(title, description, category, tags)
            
            return {
                "category": category,
                "tags": tags,
                "filename": filename,
                "frontmatter": frontmatter
            }
            
        except Exception as e:
            logger.error(f"Failed to generate fallback metadata: {e}")
            return {
                "category": "development",
                "tags": ["blog", "article"],
                "filename": "blog-post.md",
                "frontmatter": {
                    "title": title,
                    "description": description,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "draft": True,
                    "taxonomies": {
                        "categories": ["development"],
                        "tags": ["blog", "article"]
                    }
                }
            }
    
    def _generate_fallback_frontmatter(self, title: str, description: str, category: str, tags: List[str]) -> Dict[str, Any]:
        """Generate fallback frontmatter."""
        try:
            return {
                "title": title,
                "description": description,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "draft": True,
                "taxonomies": {
                    "categories": [category],
                    "tags": tags
                }
            }
        except Exception as e:
            logger.error(f"Failed to generate fallback frontmatter: {e}")
            return {
                "title": title,
                "description": description,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "draft": True,
                "taxonomies": {
                    "categories": ["development"],
                    "tags": ["blog", "article"]
                }
            } 