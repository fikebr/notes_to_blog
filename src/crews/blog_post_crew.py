"""
Blog Post Crew for orchestrating the complete blog post creation workflow.

This crew coordinates all agents (Content Analyzer, Research, Content Writer,
Image Generator, Metadata Generator) to transform raw notes into comprehensive
blog posts with proper structure, research, content, images, and metadata.
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from crewai import Crew, Task
from pydantic import BaseModel

from src.models.config_models import Config
from src.models.blog_models import BlogPost, Note, Image, FrontMatter
from src.services import ServiceRegistry
from src.agents import (
    ContentAnalyzerAgent, ResearchAgent, ContentWriterAgent,
    ImageGeneratorAgent, MetadataGeneratorAgent
)

logger = logging.getLogger(__name__)


class WorkflowStep(BaseModel):
    """Represents a step in the blog post creation workflow."""
    
    step_number: int
    name: str
    description: str
    status: str = "pending"  # pending, in_progress, completed, failed
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None


class BlogPostCrew:
    """Crew for orchestrating blog post creation from raw notes."""
    
    def __init__(self, config: Config, service_registry: ServiceRegistry):
        """Initialize the blog post crew."""
        self.config = config
        self.service_registry = service_registry
        self.workflow_steps: List[WorkflowStep] = []
        
        # Initialize all agents
        self.content_analyzer = ContentAnalyzerAgent(config, service_registry)
        self.researcher = ResearchAgent(config, service_registry)
        self.content_writer = ContentWriterAgent(config, service_registry)
        self.image_generator = ImageGeneratorAgent(config, service_registry)
        self.metadata_generator = MetadataGeneratorAgent(config, service_registry)
        
        # Initialize workflow steps
        self._initialize_workflow_steps()
        
        logger.info("Blog Post Crew initialized with all agents")
    
    def _initialize_workflow_steps(self):
        """Initialize the 15-step workflow process."""
        steps = [
            (1, "Input Validation", "Validate and parse input notes"),
            (2, "Content Analysis", "Analyze notes and create outline"),
            (3, "Title Generation", "Generate compelling blog post title"),
            (4, "Description Creation", "Create engaging description"),
            (5, "Subheading Planning", "Plan logical subheading structure"),
            (6, "Research Coordination", "Coordinate research for each subheading"),
            (7, "Content Research", "Research content for subheadings"),
            (8, "Source Validation", "Validate and cite sources"),
            (9, "Introduction Writing", "Write compelling introduction"),
            (10, "Content Expansion", "Expand subheadings with research"),
            (11, "Conclusion Writing", "Write engaging conclusion"),
            (12, "Image Planning", "Plan and create image prompts"),
            (13, "Image Generation", "Generate and store images"),
            (14, "Metadata Creation", "Create SEO-optimized metadata"),
            (15, "Output Generation", "Generate final blog post file")
        ]
        
        self.workflow_steps = [
            WorkflowStep(step_number=num, name=name, description=desc)
            for num, name, desc in steps
        ]
    
    def create_blog_post(self, notes_content: str, notes_filename: str = "notes.txt") -> BlogPost:
        """Create a complete blog post from raw notes."""
        try:
            logger.info(f"Starting blog post creation from {notes_filename}")
            
            # Step 1: Input Validation
            self._update_step_status(1, "in_progress")
            validated_notes = self._validate_input(notes_content, notes_filename)
            self._update_step_status(1, "completed", result={"notes": validated_notes})
            
            # Step 2: Content Analysis
            self._update_step_status(2, "in_progress")
            analysis_result = self.content_analyzer.analyze_notes(validated_notes.content)
            self._update_step_status(2, "completed", result=analysis_result)
            
            # Step 3: Title Generation
            self._update_step_status(3, "in_progress")
            title = analysis_result.get("title", "Generated Blog Post Title")
            self._update_step_status(3, "completed", result={"title": title})
            
            # Step 4: Description Creation
            self._update_step_status(4, "in_progress")
            description = analysis_result.get("description", "Generated description")
            self._update_step_status(4, "completed", result={"description": description})
            
            # Step 5: Subheading Planning
            self._update_step_status(5, "in_progress")
            subheadings = analysis_result.get("subheadings", ["Introduction", "Main Content", "Conclusion"])
            self._update_step_status(5, "completed", result={"subheadings": subheadings})
            
            # Step 6: Research Coordination
            self._update_step_status(6, "in_progress")
            research_data = self._coordinate_research(title, subheadings)
            self._update_step_status(6, "completed", result={"research_data": research_data})
            
            # Step 7: Content Research
            self._update_step_status(7, "in_progress")
            expanded_research = self._research_content(subheadings, research_data)
            self._update_step_status(7, "completed", result={"expanded_research": expanded_research})
            
            # Step 8: Source Validation
            self._update_step_status(8, "in_progress")
            validated_sources = self._validate_sources(expanded_research)
            self._update_step_status(8, "completed", result={"validated_sources": validated_sources})
            
            # Step 9: Introduction Writing
            self._update_step_status(9, "in_progress")
            introduction = self.content_writer.write_introduction(title, description)
            self._update_step_status(9, "completed", result={"introduction": introduction})
            
            # Step 10: Content Expansion
            self._update_step_status(10, "in_progress")
            expanded_content = self._expand_content(subheadings, expanded_research)
            self._update_step_status(10, "completed", result={"expanded_content": expanded_content})
            
            # Step 11: Conclusion Writing
            self._update_step_status(11, "in_progress")
            conclusion = self.content_writer.write_conclusion(title, list(expanded_content.keys()))
            self._update_step_status(11, "completed", result={"conclusion": conclusion})
            
            # Step 12: Image Planning
            self._update_step_status(12, "in_progress")
            image_prompts = self.image_generator.create_image_prompts(title, str(expanded_content), subheadings)
            self._update_step_status(12, "completed", result={"image_prompts": image_prompts})
            
            # Step 13: Image Generation
            self._update_step_status(13, "in_progress")
            generated_images = self.image_generator.generate_images(image_prompts)
            self._update_step_status(13, "completed", result={"generated_images": generated_images})
            
            # Step 14: Metadata Creation
            self._update_step_status(14, "in_progress")
            metadata = self.metadata_generator.generate_metadata(title, description, str(expanded_content))
            self._update_step_status(14, "completed", result={"metadata": metadata})
            
            # Step 15: Output Generation
            self._update_step_status(15, "in_progress")
            blog_post = self._generate_final_output(
                title, description, introduction, expanded_content, conclusion,
                generated_images, metadata
            )
            self._update_step_status(15, "completed", result={"blog_post": blog_post})
            
            logger.info("Blog post creation completed successfully")
            return blog_post
            
        except Exception as e:
            logger.error(f"Blog post creation failed: {e}")
            self._handle_workflow_error(e)
            raise
    
    def _validate_input(self, notes_content: str, filename: str) -> Note:
        """Validate and parse input notes."""
        try:
            # Create Note object with validation
            note = Note(
                content=notes_content,
                filename=filename,
                created_at=datetime.now(),
                source="inbox"
            )
            
            logger.info(f"Input validation successful for {filename}")
            return note
            
        except Exception as e:
            logger.error(f"Input validation failed: {e}")
            raise
    
    def _coordinate_research(self, title: str, subheadings: List[str]) -> Dict[str, Any]:
        """Coordinate research for the blog post."""
        try:
            research_data = {}
            
            # Research main topic
            main_research = self.researcher.research_topic(title)
            research_data["main_topic"] = main_research
            
            # Research each subheading
            for subheading in subheadings:
                subheading_research = self.researcher.research_subheading(subheading, title)
                research_data[subheading] = subheading_research
            
            logger.info(f"Research coordination completed for {len(subheadings)} subheadings")
            return research_data
            
        except Exception as e:
            logger.error(f"Research coordination failed: {e}")
            raise
    
    def _research_content(self, subheadings: List[str], research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Expand research content for each subheading."""
        try:
            expanded_research = {}
            
            for subheading in subheadings:
                if subheading in research_data:
                    # Combine main topic research with subheading-specific research
                    main_research = research_data.get("main_topic", {})
                    subheading_research = research_data.get(subheading, {})
                    
                    expanded_research[subheading] = {
                        "main_context": main_research,
                        "subheading_research": subheading_research,
                        "combined_summary": f"{main_research.get('summary', '')} {subheading_research.get('summary', '')}",
                        "key_points": main_research.get("key_points", []) + subheading_research.get("key_points", []),
                        "sources": main_research.get("sources", []) + subheading_research.get("sources", [])
                    }
            
            logger.info(f"Content research completed for {len(subheadings)} subheadings")
            return expanded_research
            
        except Exception as e:
            logger.error(f"Content research failed: {e}")
            raise
    
    def _validate_sources(self, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate sources from research data."""
        try:
            validated_data = {}
            
            for subheading, data in research_data.items():
                sources = data.get("sources", [])
                validated_sources = self.researcher.validate_sources(sources)
                
                validated_data[subheading] = {
                    **data,
                    "validated_sources": validated_sources,
                    "citations": self.researcher.generate_citations(data)
                }
            
            logger.info("Source validation completed")
            return validated_data
            
        except Exception as e:
            logger.error(f"Source validation failed: {e}")
            raise
    
    def _expand_content(self, subheadings: List[str], research_data: Dict[str, Any]) -> Dict[str, str]:
        """Expand content for each subheading."""
        try:
            expanded_content = {}
            
            for subheading in subheadings:
                if subheading in research_data:
                    content = self.content_writer.expand_subheading(
                        subheading, research_data[subheading]
                    )
                    expanded_content[subheading] = content
            
            logger.info(f"Content expansion completed for {len(subheadings)} subheadings")
            return expanded_content
            
        except Exception as e:
            logger.error(f"Content expansion failed: {e}")
            raise
    
    def _generate_final_output(
        self, title: str, description: str, introduction: str,
        expanded_content: Dict[str, str], conclusion: str,
        generated_images: Dict[str, Dict[str, str]], metadata: Dict[str, Any]
    ) -> BlogPost:
        """Generate the final blog post output."""
        try:
            # Create frontmatter
            frontmatter = FrontMatter(
                title=title,
                description=description,
                date=datetime.now().strftime("%Y-%m-%d"),
                draft=True,
                categories=[metadata.get("category", "development")],
                tags=metadata.get("tags", ["blog", "article"])
            )
            
            # Combine content
            content_sections = []
            content_sections.append(introduction)
            
            for subheading, content in expanded_content.items():
                content_sections.append(f"## {subheading}\n\n{content}")
            
            content_sections.append(f"## Conclusion\n\n{conclusion}")
            
            # Add image placeholders
            if generated_images:
                content_sections.append("\n\n## Image Placeholders\n")
                for image_key, image_data in generated_images.items():
                    content_sections.append(f"### {image_key.replace('_', ' ').title()}")
                    content_sections.append(f"**Prompt:** {image_data['prompt']}")
                    content_sections.append(f"**Placeholder:** {image_data['placeholder']}")
                    content_sections.append(f"**Alt Text:** {image_data['alt_text']}")
                    content_sections.append("")
            
            full_content = "\n\n".join(content_sections)
            
            # Create blog post without Image objects (since we're using placeholders)
            blog_post = BlogPost(
                frontmatter=frontmatter,
                content=full_content,
                filename=metadata.get("filename", f"{title.lower().replace(' ', '-')}.md"),
                created_at=datetime.now(),
                images=[]  # No actual images, just placeholders in content
            )
            
            logger.info("Final blog post output generated successfully with image placeholders")
            return blog_post
            
        except Exception as e:
            logger.error(f"Final output generation failed: {e}")
            raise
    
    def _update_step_status(self, step_number: int, status: str, result: Optional[Dict[str, Any]] = None):
        """Update the status of a workflow step."""
        try:
            step = next((s for s in self.workflow_steps if s.step_number == step_number), None)
            if step:
                step.status = status
                if status == "in_progress":
                    step.start_time = datetime.now()
                elif status in ["completed", "failed"]:
                    step.end_time = datetime.now()
                    if result:
                        step.result = result
                
                logger.info(f"Step {step_number} ({step.name}): {status}")
            
        except Exception as e:
            logger.error(f"Failed to update step status: {e}")
    
    def _handle_workflow_error(self, error: Exception):
        """Handle workflow errors and update step status."""
        try:
            # Find the current step (first step with in_progress status)
            current_step = next((s for s in self.workflow_steps if s.status == "in_progress"), None)
            if current_step:
                current_step.status = "failed"
                current_step.end_time = datetime.now()
                current_step.error_message = str(error)
                logger.error(f"Workflow failed at step {current_step.step_number}: {error}")
            
        except Exception as e:
            logger.error(f"Failed to handle workflow error: {e}")
    
    def get_workflow_status(self) -> List[Dict[str, Any]]:
        """Get the current status of all workflow steps."""
        try:
            return [
                {
                    "step_number": step.step_number,
                    "name": step.name,
                    "status": step.status,
                    "start_time": step.start_time.isoformat() if step.start_time else None,
                    "end_time": step.end_time.isoformat() if step.end_time else None,
                    "error_message": step.error_message
                }
                for step in self.workflow_steps
            ]
        except Exception as e:
            logger.error(f"Failed to get workflow status: {e}")
            return []
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check of the crew and all agents."""
        try:
            agent_health = {
                "content_analyzer": self.content_analyzer.health_check(),
                "researcher": self.researcher.health_check(),
                "content_writer": self.content_writer.health_check(),
                "image_generator": self.image_generator.health_check(),
                "metadata_generator": self.metadata_generator.health_check()
            }
            
            return {
                "crew_name": "Blog Post Crew",
                "status": "healthy",
                "agents": agent_health,
                "workflow_steps": len(self.workflow_steps),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "crew_name": "Blog Post Crew",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            } 