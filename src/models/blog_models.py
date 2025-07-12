"""
Blog post data models for the Notes to Blog application.

This module contains all Pydantic models related to blog posts, notes, images,
and content management.
"""

from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field, field_validator, HttpUrl


class Category(BaseModel):
    """Blog post category model."""
    
    name: str = Field(..., description="Category name", min_length=1, max_length=50)
    slug: str = Field(..., description="URL-friendly category slug", min_length=1, max_length=50)
    description: Optional[str] = Field(None, description="Category description", max_length=200)
    
    @field_validator('slug', mode='after')
    def validate_slug(cls, v: str) -> str:
        """Validate slug format."""
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError("Slug must contain only alphanumeric characters, hyphens, and underscores")
        return v.lower()


class Tag(BaseModel):
    """Blog post tag model."""
    
    name: str = Field(..., description="Tag name", min_length=1, max_length=30)
    slug: str = Field(..., description="URL-friendly tag slug", min_length=1, max_length=30)
    
    @field_validator('slug', mode='after')
    def validate_slug(cls, v: str) -> str:
        """Validate slug format."""
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError("Slug must contain only alphanumeric characters, hyphens, and underscores")
        return v.lower()


class Image(BaseModel):
    """Generated image model."""
    
    filename: str = Field(..., description="Image filename")
    file_path: Path = Field(..., description="Path to image file")
    prompt: str = Field(..., description="Prompt used to generate image", min_length=10)
    alt_text: str = Field(..., description="Alt text for accessibility", min_length=5, max_length=200)
    width: int = Field(..., description="Image width in pixels", ge=256, le=2048)
    height: int = Field(..., description="Image height in pixels", ge=256, le=2048)
    file_size: Optional[int] = Field(None, description="File size in bytes")
    generated_at: datetime = Field(default_factory=datetime.now, description="Generation timestamp")
    model_used: str = Field(..., description="AI model used for generation")
    
    @field_validator('filename', mode='after')
    def validate_filename(cls, v: str) -> str:
        """Validate filename format."""
        if not v.endswith(('.jpg', '.jpeg', '.png', '.webp')):
            raise ValueError("Filename must end with .jpg, .jpeg, .png, or .webp")
        return v
    
    @field_validator('file_path', mode='after')
    def validate_file_path(cls, v: Path) -> Path:
        """Ensure file path is absolute and exists."""
        if not v.is_absolute():
            v = v.resolve()
        return v


class FrontMatter(BaseModel):
    """Blog post frontmatter model."""
    
    title: str = Field(..., description="Blog post title", min_length=5, max_length=200)
    description: str = Field(..., description="Blog post description", min_length=10, max_length=500)
    date: datetime = Field(default_factory=datetime.now, description="Publication date")
    draft: bool = Field(default=True, description="Draft status")
    categories: List[str] = Field(..., description="Post categories", min_length=1, max_length=3)
    tags: List[str] = Field(..., description="Post tags", min_length=2, max_length=10)
    author: Optional[str] = Field(None, description="Post author")
    featured_image: Optional[str] = Field(None, description="Featured image filename")
    
    @field_validator('title', mode='after')
    def validate_title(cls, v: str) -> str:
        """Validate title format."""
        if len(v.strip()) < 5:
            raise ValueError("Title must be at least 5 characters long")
        return v.strip()
    
    @field_validator('description', mode='after')
    def validate_description(cls, v: str) -> str:
        """Validate description format."""
        if len(v.strip()) < 10:
            raise ValueError("Description must be at least 10 characters long")
        return v.strip()
    
    @field_validator('categories', mode='after')
    def validate_categories(cls, v: List[str]) -> List[str]:
        """Validate categories."""
        if not v:
            raise ValueError("At least one category is required")
        if len(v) > 3:
            raise ValueError("Maximum 3 categories allowed")
        return [cat.strip().lower() for cat in v if cat.strip()]
    
    @field_validator('tags', mode='after')
    def validate_tags(cls, v: List[str]) -> List[str]:
        """Validate tags."""
        if len(v) < 2:
            raise ValueError("At least 2 tags are required")
        if len(v) > 10:
            raise ValueError("Maximum 10 tags allowed")
        return [tag.strip().lower() for tag in v if tag.strip()]


class Note(BaseModel):
    """Input note model for processing."""
    
    content: str = Field(..., description="Raw note content", min_length=10)
    source_file: Optional[Path] = Field(None, description="Source file path")
    title: Optional[str] = Field(None, description="Note title", max_length=200)
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    filename: Optional[str] = Field(None, description="Original filename if available")
    
    @field_validator('content', mode='after')
    def validate_content(cls, v: str) -> str:
        """Validate content format."""
        if len(v.strip()) < 10:
            raise ValueError("Note content must be at least 10 characters long")
        return v.strip()
    
    @field_validator('title', mode='after')
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        """Validate title if provided."""
        if v is not None and len(v.strip()) < 3:
            raise ValueError("Title must be at least 3 characters long if provided")
        return v.strip() if v else None
    
    @field_validator('filename', mode='after')
    def validate_filename(cls, v: Optional[str]) -> Optional[str]:
        """Validate filename if provided."""
        if v is not None and len(v.strip()) < 3:
            raise ValueError("Filename must be at least 3 characters long if provided")
        return v.strip() if v else None


class Subheading(BaseModel):
    """Blog post subheading model."""
    
    title: str = Field(..., description="Subheading title", min_length=3, max_length=100)
    content: str = Field(..., description="Subheading content", min_length=50)
    order: int = Field(..., description="Subheading order", ge=1)
    word_count: Optional[int] = Field(None, description="Word count")
    
    @field_validator('title', mode='after')
    def validate_title(cls, v: str) -> str:
        """Validate title format."""
        if len(v.strip()) < 3:
            raise ValueError("Subheading title must be at least 3 characters long")
        return v.strip()
    
    @field_validator('content', mode='after')
    def validate_content(cls, v: str) -> str:
        """Validate content format."""
        if len(v.strip()) < 50:
            raise ValueError("Subheading content must be at least 50 characters long")
        return v.strip()


class BlogPost(BaseModel):
    """Complete blog post model."""
    
    frontmatter: FrontMatter = Field(..., description="Post frontmatter")
    content: str = Field(..., description="Main post content", min_length=100)
    subheadings: List[Subheading] = Field(default_factory=list, description="Post subheadings")
    images: List[Image] = Field(default_factory=list, description="Post images")
    introduction: str = Field(..., description="Post introduction", min_length=50)
    conclusion: str = Field(..., description="Post conclusion", min_length=50)
    filename: str = Field(..., description="Output filename")
    output_path: Path = Field(..., description="Output file path")
    word_count: Optional[int] = Field(None, description="Total word count")
    reading_time: Optional[int] = Field(None, description="Estimated reading time in minutes")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    @field_validator('content', mode='after')
    def validate_content(cls, v: str) -> str:
        """Validate content format."""
        if len(v.strip()) < 100:
            raise ValueError("Blog post content must be at least 100 characters long")
        return v.strip()
    
    @field_validator('introduction', mode='after')
    def validate_introduction(cls, v: str) -> str:
        """Validate introduction format."""
        if len(v.strip()) < 50:
            raise ValueError("Introduction must be at least 50 characters long")
        return v.strip()
    
    @field_validator('conclusion', mode='after')
    def validate_conclusion(cls, v: str) -> str:
        """Validate conclusion format."""
        if len(v.strip()) < 50:
            raise ValueError("Conclusion must be at least 50 characters long")
        return v.strip()
    
    @field_validator('filename', mode='after')
    def validate_filename(cls, v: str) -> str:
        """Validate filename format."""
        if not v.endswith('.md'):
            raise ValueError("Filename must end with .md")
        if len(v) < 5:
            raise ValueError("Filename must be at least 5 characters long")
        return v
    
    @field_validator('subheadings', mode='after')
    def validate_subheadings(cls, v: List[Subheading]) -> List[Subheading]:
        """Validate subheadings order and count."""
        if len(v) < 2:
            raise ValueError("At least 2 subheadings are required")
        if len(v) > 10:
            raise ValueError("Maximum 10 subheadings allowed")
        
        # Check order sequence
        orders = [sh.order for sh in v]
        if orders != sorted(orders):
            raise ValueError("Subheadings must be in ascending order")
        
        return v
    
    @field_validator('images', mode='after')
    def validate_images(cls, v: List[Image]) -> List[Image]:
        """Validate images count."""
        if len(v) > 10:
            raise ValueError("Maximum 10 images allowed per post")
        return v
    
    def calculate_word_count(self) -> int:
        """Calculate total word count."""
        total = len(self.content.split())
        total += len(self.introduction.split())
        total += len(self.conclusion.split())
        for subheading in self.subheadings:
            total += len(subheading.content.split())
        return total
    
    def calculate_reading_time(self) -> int:
        """Calculate estimated reading time in minutes."""
        word_count = self.word_count or self.calculate_word_count()
        # Average reading speed: 200 words per minute
        return max(1, word_count // 200)
    
    def to_markdown(self) -> str:
        """Convert blog post to markdown format."""
        # Frontmatter
        frontmatter_lines = [
            "+++",
            f'title = "{self.frontmatter.title}"',
            f'description = "{self.frontmatter.description}"',
            f'date = {self.frontmatter.date.strftime("%Y-%m-%d")}',
            f'draft = {str(self.frontmatter.draft).lower()}',
            "",
            "[taxonomies]",
            f'categories = ["{", ".join(self.frontmatter.categories)}"]',
            f'tags = ["{", ".join(self.frontmatter.tags)}"]',
            "+++",
            ""
        ]
        
        # Content
        content_lines = [
            self.introduction,
            ""
        ]
        
        # Subheadings
        for subheading in self.subheadings:
            content_lines.extend([
                f"## {subheading.title}",
                "",
                subheading.content,
                ""
            ])
        
        # Conclusion
        content_lines.extend([
            self.conclusion,
            ""
        ])
        
        return "\n".join(frontmatter_lines + content_lines) 