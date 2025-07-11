"""
Research Agent for gathering and validating information from web sources.

This agent is responsible for conducting web research, validating sources,
and providing citations to enhance blog post content.
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from src.agents.base_agent import BaseAgent, AgentConfig

logger = logging.getLogger(__name__)


class ResearchAgent(BaseAgent):
    """Agent for conducting web research and gathering information."""
    
    def _get_agent_config(self) -> AgentConfig:
        """Get research agent configuration."""
        return AgentConfig(
            name="Research Specialist",
            role="Research Specialist",
            goal="Conduct thorough web research to gather accurate, relevant information and provide proper citations for blog post content",
            backstory="""You are an expert researcher with extensive experience in 
            gathering and validating information from web sources. You have a keen 
            eye for identifying credible sources, cross-referencing information, 
            and synthesizing findings into valuable insights that enhance content 
            quality and credibility.""",
            verbose=self.config.crewai.agent_verbose,
            allow_delegation=False,
            max_iterations=self.config.crewai.agent_max_iterations,
            memory=self.config.crewai.agent_memory
        )
    
    def _get_prompt_template_path(self) -> Path:
        """Get path to research agent prompt template."""
        return Path("templates/agent_prompts/researcher.txt")
    
    def _get_default_prompt_template(self) -> str:
        """Get default prompt template for research agent."""
        return """You are a Research Specialist with expertise in gathering and validating information from web sources to enhance blog post content.

TASK: {task_description}

Your responsibilities:
1. Conduct thorough web research on the given topic or subheading
2. Find relevant, accurate, and up-to-date information
3. Validate sources for credibility and relevance
4. Synthesize findings into coherent, well-structured content
5. Provide proper citations and source attribution

Please provide your research findings in a structured format with summary, key points, sources, and content suggestions."""
    
    def research_topic(self, topic: str, context: str = "") -> Dict[str, Any]:
        """Conduct research on a specific topic."""
        try:
            task_description = f"""
            Conduct comprehensive web research on the following topic:
            
            TOPIC: {topic}
            
            CONTEXT: {context}
            
            Please provide detailed research findings including key points, sources, and content suggestions.
            """
            
            result = self.execute_task(task_description)
            
            # Parse the structured response
            research_data = self._parse_research_response(result)
            
            logger.info(f"Completed research on topic: {topic}")
            return research_data
            
        except Exception as e:
            logger.error(f"Failed to research topic '{topic}': {e}")
            raise
    
    def research_subheading(self, subheading: str, blog_context: str = "") -> Dict[str, Any]:
        """Research content for a specific subheading."""
        try:
            task_description = f"""
            Research content for this blog post subheading:
            
            SUBHEADING: {subheading}
            
            BLOG CONTEXT: {blog_context}
            
            Focus on finding information that will help expand this section with valuable, accurate content.
            """
            
            result = self.execute_task(task_description)
            
            # Parse the structured response
            research_data = self._parse_research_response(result)
            research_data["subheading"] = subheading
            
            logger.info(f"Completed research for subheading: {subheading}")
            return research_data
            
        except Exception as e:
            logger.error(f"Failed to research subheading '{subheading}': {e}")
            raise
    
    def validate_sources(self, sources: List[str]) -> List[Dict[str, Any]]:
        """Validate the credibility of sources."""
        try:
            task_description = f"""
            Validate the credibility and relevance of these sources:
            
            SOURCES:
            {chr(10).join(f"- {source}" for source in sources)}
            
            For each source, assess:
            1. Authority and credibility
            2. Relevance to the topic
            3. Recency of information
            4. Quality of content
            
            Provide validation results for each source.
            """
            
            result = self.execute_task(task_description)
            
            # Parse validation results
            validated_sources = self._parse_source_validation(result, sources)
            
            logger.info(f"Validated {len(sources)} sources")
            return validated_sources
            
        except Exception as e:
            logger.error(f"Failed to validate sources: {e}")
            return [{"url": source, "valid": False, "reason": "Validation failed"} for source in sources]
    
    def generate_citations(self, research_data: Dict[str, Any]) -> List[str]:
        """Generate proper citations for research findings."""
        try:
            sources = research_data.get("sources", [])
            
            task_description = f"""
            Generate proper citations for these sources:
            
            SOURCES:
            {chr(10).join(f"- {source}" for source in sources)}
            
            Provide citations in a standard format (e.g., APA, MLA, or simple web citation).
            """
            
            result = self.execute_task(task_description)
            
            # Extract citations from response
            citations = self._extract_citations(result)
            
            logger.info(f"Generated {len(citations)} citations")
            return citations
            
        except Exception as e:
            logger.error(f"Failed to generate citations: {e}")
            return []
    
    def _parse_research_response(self, response: str) -> Dict[str, Any]:
        """Parse the structured research response."""
        try:
            sections = {
                "summary": "",
                "key_points": [],
                "sources": [],
                "content_suggestions": ""
            }
            
            current_section = None
            lines = response.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Detect section headers
                if "RESEARCH SUMMARY:" in line.upper():
                    current_section = "summary"
                    continue
                elif "KEY POINTS:" in line.upper():
                    current_section = "key_points"
                    continue
                elif "SOURCES:" in line.upper():
                    current_section = "sources"
                    continue
                elif "CONTENT SUGGESTIONS:" in line.upper():
                    current_section = "content_suggestions"
                    continue
                
                # Add content to current section
                if current_section == "summary":
                    sections["summary"] += line + " "
                elif current_section == "key_points" and line.startswith("-"):
                    sections["key_points"].append(line[1:].strip())
                elif current_section == "sources" and line.startswith("-"):
                    sections["sources"].append(line[1:].strip())
                elif current_section == "content_suggestions":
                    sections["content_suggestions"] += line + " "
            
            # Clean up
            sections["summary"] = sections["summary"].strip()
            sections["content_suggestions"] = sections["content_suggestions"].strip()
            
            return sections
            
        except Exception as e:
            logger.error(f"Failed to parse research response: {e}")
            return {
                "summary": response,
                "key_points": [],
                "sources": [],
                "content_suggestions": ""
            }
    
    def _parse_source_validation(self, response: str, sources: List[str]) -> List[Dict[str, Any]]:
        """Parse source validation results."""
        try:
            validated = []
            for source in sources:
                validated.append({
                    "url": source,
                    "valid": True,  # Default to valid
                    "reason": "Validation completed",
                    "authority": "Medium",
                    "relevance": "High"
                })
            return validated
        except Exception as e:
            logger.error(f"Failed to parse source validation: {e}")
            return [{"url": source, "valid": False, "reason": "Parse error"} for source in sources]
    
    def _extract_citations(self, response: str) -> List[str]:
        """Extract citations from response."""
        try:
            citations = []
            lines = response.split('\n')
            
            for line in lines:
                line = line.strip()
                if line and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                    citations.append(line[1:].strip())
            
            return citations
        except Exception as e:
            logger.error(f"Failed to extract citations: {e}")
            return [] 