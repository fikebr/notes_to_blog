"""
Content Writer Agent for creating engaging blog post content.

This agent is responsible for writing introductions, conclusions, expanding
subheadings, and structuring content for optimal readability.
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from src.agents.base_agent import BaseAgent, AgentConfig

logger = logging.getLogger(__name__)


class ContentWriterAgent(BaseAgent):
    """Agent for writing and structuring blog post content."""
    
    def _get_agent_config(self) -> AgentConfig:
        """Get content writer agent configuration."""
        return AgentConfig(
            name="Content Writer",
            role="Content Writer Specialist",
            goal="Create engaging, well-structured blog post content that informs and entertains readers",
            backstory="""You are an expert content writer with years of experience in 
            creating compelling blog posts that engage readers and drive results. You 
            have a talent for transforming complex topics into accessible, enjoyable 
            content that maintains reader interest from start to finish.""",
            verbose=self.config.crewai.agent_verbose,
            allow_delegation=False,
            max_iterations=self.config.crewai.agent_max_iterations,
            memory=self.config.crewai.agent_memory
        )
    
    def _get_prompt_template_path(self) -> Path:
        """Get path to content writer prompt template."""
        return Path("templates/agent_prompts/content_writer.txt")
    
    def _get_default_prompt_template(self) -> str:
        """Get default prompt template for content writer."""
        return """You are a Content Writer Specialist with expertise in creating engaging, well-structured blog posts that inform and entertain readers.

TASK: {task_description}

Your responsibilities:
1. Write compelling introductions that hook readers
2. Expand subheadings into comprehensive, informative sections
3. Create engaging conclusions that summarize key points
4. Structure content for optimal readability and flow
5. Ensure consistent tone and style throughout the post

Focus on creating content that provides real value to readers while maintaining their interest throughout the entire post."""
    
    def write_introduction(self, title: str, description: str, context: str = "") -> str:
        """Write a compelling introduction for the blog post."""
        try:
            task_description = f"""
            Write a compelling introduction for this blog post:
            
            TITLE: {title}
            DESCRIPTION: {description}
            CONTEXT: {context}
            
            The introduction should:
            - Hook the reader immediately
            - Establish the topic and its importance
            - Preview what the reader will learn
            - Be engaging and conversational
            - Set the tone for the rest of the post
            
            Keep it concise but impactful (2-3 paragraphs).
            """
            
            result = self.execute_task(task_description)
            logger.info("Generated blog post introduction")
            return result.strip()
            
        except Exception as e:
            logger.error(f"Failed to write introduction: {e}")
            return f"Welcome to our guide on {title}. In this post, we'll explore {description}."
    
    def write_conclusion(self, title: str, key_points: List[str], context: str = "") -> str:
        """Write an engaging conclusion for the blog post."""
        try:
            key_points_text = "\n".join(f"- {point}" for point in key_points)
            
            task_description = f"""
            Write an engaging conclusion for this blog post:
            
            TITLE: {title}
            KEY POINTS: {key_points_text}
            CONTEXT: {context}
            
            The conclusion should:
            - Summarize the main takeaways
            - Reinforce the value provided
            - End with a strong call-to-action or thought-provoking statement
            - Be memorable and impactful
            - Tie back to the introduction
            
            Keep it concise but powerful (1-2 paragraphs).
            """
            
            result = self.execute_task(task_description)
            logger.info("Generated blog post conclusion")
            return result.strip()
            
        except Exception as e:
            logger.error(f"Failed to write conclusion: {e}")
            return f"Thank you for reading our guide on {title}. We hope you found this information valuable and actionable."
    
    def expand_subheading(self, subheading: str, research_data: Dict[str, Any], context: str = "") -> str:
        """Expand a subheading into comprehensive content."""
        try:
            research_summary = research_data.get("summary", "")
            key_points = research_data.get("key_points", [])
            sources = research_data.get("sources", [])
            
            task_description = f"""
            Expand this subheading into comprehensive, engaging content:
            
            SUBHEADING: {subheading}
            RESEARCH SUMMARY: {research_summary}
            KEY POINTS: {chr(10).join(f"- {point}" for point in key_points)}
            SOURCES: {chr(10).join(f"- {source}" for source in sources)}
            CONTEXT: {context}
            
            Create content that:
            - Thoroughly covers the subheading topic
            - Incorporates the research findings naturally
            - Uses examples and explanations to clarify points
            - Maintains reader engagement
            - Flows well with the overall post structure
            
            Write 2-4 paragraphs of comprehensive content.
            """
            
            result = self.execute_task(task_description)
            logger.info(f"Expanded subheading: {subheading}")
            return result.strip()
            
        except Exception as e:
            logger.error(f"Failed to expand subheading '{subheading}': {e}")
            return f"This section covers {subheading}. Additional content will be developed based on research findings."
    
    def structure_content(self, sections: Dict[str, str]) -> str:
        """Structure and format the complete blog post content."""
        try:
            sections_text = "\n\n".join([
                f"## {heading}\n{content}" 
                for heading, content in sections.items()
            ])
            
            task_description = f"""
            Structure and format this blog post content for optimal readability:
            
            CONTENT SECTIONS:
            {sections_text}
            
            Please:
            - Ensure proper markdown formatting
            - Add appropriate spacing and transitions
            - Check for logical flow between sections
            - Optimize paragraph breaks for readability
            - Ensure consistent formatting throughout
            
            Return the complete, well-structured blog post content.
            """
            
            result = self.execute_task(task_description)
            logger.info("Structured complete blog post content")
            return result.strip()
            
        except Exception as e:
            logger.error(f"Failed to structure content: {e}")
            # Fallback: simple concatenation
            return "\n\n".join([
                f"## {heading}\n\n{content}" 
                for heading, content in sections.items()
            ])
    
    def write_complete_post(self, title: str, description: str, subheadings: List[str], 
                           research_data: Dict[str, Any]) -> str:
        """Write a complete blog post from start to finish."""
        try:
            # Write introduction
            introduction = self.write_introduction(title, description)
            
            # Expand each subheading
            sections = {}
            for subheading in subheadings:
                subheading_research = research_data.get(subheading, {})
                content = self.expand_subheading(subheading, subheading_research)
                sections[subheading] = content
            
            # Write conclusion
            key_points = [f"Key point about {subheading}" for subheading in subheadings]
            conclusion = self.write_conclusion(title, key_points)
            
            # Structure complete content
            complete_content = f"""
# {title}

{introduction}

{self.structure_content(sections)}

## Conclusion

{conclusion}
"""
            
            logger.info("Generated complete blog post")
            return complete_content.strip()
            
        except Exception as e:
            logger.error(f"Failed to write complete post: {e}")
            raise
    
    def optimize_for_seo(self, content: str, keywords: List[str]) -> str:
        """Optimize content for SEO with given keywords."""
        try:
            keywords_text = ", ".join(keywords)
            
            task_description = f"""
            Optimize this blog post content for SEO with these keywords:
            
            KEYWORDS: {keywords_text}
            
            CONTENT:
            {content}
            
            Please:
            - Naturally incorporate keywords throughout the content
            - Ensure keyword density is appropriate (not over-optimized)
            - Maintain readability and flow
            - Add relevant internal linking suggestions
            - Optimize headings and subheadings for SEO
            
            Return the SEO-optimized content.
            """
            
            result = self.execute_task(task_description)
            logger.info(f"Optimized content for SEO with keywords: {keywords}")
            return result.strip()
            
        except Exception as e:
            logger.error(f"Failed to optimize for SEO: {e}")
            return content 