"""
Content Analyzer Agent for processing and analyzing raw notes.

This agent is responsible for analyzing input notes and creating structured
blog post outlines with titles, descriptions, and subheadings.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List

from src.agents.base_agent import BaseAgent, AgentConfig

logger = logging.getLogger(__name__)


class ContentAnalyzerAgent(BaseAgent):
    """Agent for analyzing content and creating blog post outlines."""
    
    def _get_agent_config(self) -> AgentConfig:
        """Get content analyzer agent configuration."""
        return AgentConfig(
            name="Content Analyzer",
            role="Content Analysis Specialist",
            goal="Analyze raw notes and create structured blog post outlines with compelling titles, descriptions, and logical subheadings",
            backstory="""You are an expert content analyst with years of experience in 
            transforming raw notes into engaging blog post structures. You have a keen 
            eye for identifying key themes, creating compelling titles, and organizing 
            content in ways that maximize reader engagement and SEO value.""",
            verbose=self.config.crewai.agent_verbose,
            allow_delegation=False,
            max_iterations=self.config.crewai.agent_max_iterations,
            memory=self.config.crewai.agent_memory
        )
    
    def _get_prompt_template_path(self) -> Path:
        """Get path to content analyzer prompt template."""
        return Path("templates/agent_prompts/content_analyzer.txt")
    
    def _get_default_prompt_template(self) -> str:
        """Get default prompt template for content analyzer."""
        return """You are a Content Analysis Specialist with expertise in analyzing raw notes and transforming them into structured blog post outlines.

TASK: {task_description}

Your responsibilities:
1. Analyze the provided notes content thoroughly
2. Create a compelling blog post title that captures the main topic
3. Write a concise but engaging description (2-3 sentences)
4. Generate an outline with 2-5 logical subheadings that flow naturally
5. Ensure the content structure makes sense for readers

Please provide your analysis in the following JSON format:
{{
    "title": "Your suggested blog post title",
    "description": "Your suggested description (2-3 sentences)",
    "subheadings": [
        "First subheading",
        "Second subheading", 
        "Third subheading"
    ],
    "analysis_notes": "Any additional insights about the content structure"
}}"""
    
    def analyze_notes(self, notes_content: str) -> Dict[str, Any]:
        """Analyze raw notes and create blog post outline."""
        try:
            task_description = f"""
            Analyze the following raw notes and create a structured blog post outline:
            
            NOTES CONTENT:
            {notes_content}
            
            Please provide a comprehensive analysis including title, description, and subheadings.
            """
            
            result = self.execute_task(task_description)
            
            # Try to parse JSON response
            try:
                analysis = json.loads(result)
                logger.info("Successfully analyzed notes content")
                return analysis
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON response, returning raw result")
                return {
                    "title": "Generated Title",
                    "description": "Generated description",
                    "subheadings": ["Introduction", "Main Content", "Conclusion"],
                    "analysis_notes": result,
                    "raw_response": result
                }
                
        except Exception as e:
            logger.error(f"Failed to analyze notes: {e}")
            raise
    
    def generate_title(self, notes_content: str) -> str:
        """Generate a blog post title from notes content."""
        try:
            task_description = f"""
            Generate a compelling, SEO-friendly blog post title from these notes:
            
            {notes_content}
            
            Focus only on creating the title. Make it engaging and descriptive.
            """
            
            result = self.execute_task(task_description)
            return result.strip()
            
        except Exception as e:
            logger.error(f"Failed to generate title: {e}")
            return "Blog Post Title"
    
    def generate_description(self, notes_content: str) -> str:
        """Generate a blog post description from notes content."""
        try:
            task_description = f"""
            Generate a concise, engaging description (2-3 sentences) for a blog post based on these notes:
            
            {notes_content}
            
            Focus on summarizing the key value proposition and main points.
            """
            
            result = self.execute_task(task_description)
            return result.strip()
            
        except Exception as e:
            logger.error(f"Failed to generate description: {e}")
            return "Blog post description."
    
    def generate_subheadings(self, notes_content: str, num_subheadings: int = 3) -> List[str]:
        """Generate subheadings for a blog post from notes content."""
        try:
            task_description = f"""
            Generate {num_subheadings} logical subheadings for a blog post based on these notes:
            
            {notes_content}
            
            The subheadings should follow a natural progression and cover the main topics.
            Return only the subheadings as a simple list.
            """
            
            result = self.execute_task(task_description)
            
            # Try to extract subheadings from the response
            lines = result.strip().split('\n')
            subheadings = []
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#') and len(line) > 3:
                    # Remove common prefixes
                    for prefix in ['- ', '* ', '1. ', '2. ', '3. ', '4. ', '5. ']:
                        if line.startswith(prefix):
                            line = line[len(prefix):]
                            break
                    subheadings.append(line)
            
            # Ensure we have the right number of subheadings
            if len(subheadings) < num_subheadings:
                subheadings.extend([f"Section {i+1}" for i in range(len(subheadings), num_subheadings)])
            elif len(subheadings) > num_subheadings:
                subheadings = subheadings[:num_subheadings]
            
            logger.info(f"Generated {len(subheadings)} subheadings")
            return subheadings
            
        except Exception as e:
            logger.error(f"Failed to generate subheadings: {e}")
            return [f"Section {i+1}" for i in range(num_subheadings)] 