"""
Image Generator Agent for creating and managing blog post images.

This agent is responsible for creating image prompts, coordinating image
generation, and linking images in blog post content.
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from src.agents.base_agent import BaseAgent, AgentConfig

logger = logging.getLogger(__name__)


class ImageGeneratorAgent(BaseAgent):
    """Agent for generating and managing blog post images."""
    
    def _get_agent_config(self) -> AgentConfig:
        """Get image generator agent configuration."""
        return AgentConfig(
            name="Image Generator",
            role="Image Generation Specialist",
            goal="Create compelling visual prompts and coordinate image generation to enhance blog post content",
            backstory="""You are an expert in visual content creation with deep 
            understanding of how images can enhance and complement written content. 
            You have a keen eye for creating detailed, effective prompts that 
            generate engaging images that support and amplify the blog post message.""",
            verbose=self.config.crewai.agent_verbose,
            allow_delegation=False,
            max_iterations=self.config.crewai.agent_max_iterations,
            memory=self.config.crewai.agent_memory
        )
    
    def _get_prompt_template_path(self) -> Path:
        """Get path to image generator prompt template."""
        return Path("templates/agent_prompts/image_generator.txt")
    
    def _get_default_prompt_template(self) -> str:
        """Get default prompt template for image generator."""
        return """You are an Image Generation Specialist with expertise in creating compelling visual prompts for blog post images.

TASK: {task_description}

Your responsibilities:
1. Create detailed image prompts for header images
2. Generate prompts for supplemental images throughout the post
3. Ensure images are relevant and enhance the content
4. Specify appropriate image styles, compositions, and visual elements
5. Coordinate with image generation services for optimal results

Please provide image prompts in a structured format with header image, supplemental images, and style notes."""
    
    def create_image_prompts(self, title: str, content: str, subheadings: List[str]) -> Dict[str, Any]:
        """Create comprehensive image prompts for the blog post."""
        try:
            subheadings_text = "\n".join(f"- {heading}" for heading in subheadings)
            
            task_description = f"""
            Create image prompts for this blog post:
            
            TITLE: {title}
            SUBHEADINGS: {subheadings_text}
            CONTENT PREVIEW: {content[:500]}...
            
            Generate:
            1. A compelling header image prompt
            2. 2-3 supplemental image prompts for key sections
            3. Style guidance for consistency
            
            Focus on creating images that enhance reader engagement and understanding.
            """
            
            result = self.execute_task(task_description)
            
            # Parse the structured response
            image_prompts = self._parse_image_prompts(result)
            
            logger.info("Generated image prompts for blog post")
            return image_prompts
            
        except Exception as e:
            logger.error(f"Failed to create image prompts: {e}")
            raise
    
    def create_header_image_prompt(self, title: str, description: str) -> str:
        """Create a prompt for the main header image."""
        try:
            task_description = f"""
            Create a detailed image prompt for the header image of this blog post:
            
            TITLE: {title}
            DESCRIPTION: {description}
            
            The header image should:
            - Be visually striking and attention-grabbing
            - Represent the main topic effectively
            - Have a professional, high-quality appearance
            - Be suitable for blog post headers
            - Work well with text overlay if needed
            
            Provide a detailed, specific prompt that will generate an engaging header image.
            """
            
            result = self.execute_task(task_description)
            logger.info("Generated header image prompt")
            return result.strip()
            
        except Exception as e:
            logger.error(f"Failed to create header image prompt: {e}")
            return f"Professional header image representing {title}, high quality, engaging"
    
    def create_supplemental_image_prompts(self, subheadings: List[str], content: str) -> List[str]:
        """Create prompts for supplemental images throughout the post."""
        try:
            subheadings_text = "\n".join(f"- {heading}" for heading in subheadings)
            
            task_description = f"""
            Create image prompts for supplemental images to accompany these subheadings:
            
            SUBHEADINGS: {subheadings_text}
            CONTENT CONTEXT: {content[:300]}...
            
            Generate 2-3 image prompts that:
            - Complement each subheading section
            - Enhance reader understanding
            - Maintain visual consistency
            - Are relevant and engaging
            
            Provide specific, detailed prompts for each image.
            """
            
            result = self.execute_task(task_description)
            
            # Extract individual prompts
            prompts = self._extract_image_prompts(result)
            
            logger.info(f"Generated {len(prompts)} supplemental image prompts")
            return prompts
            
        except Exception as e:
            logger.error(f"Failed to create supplemental image prompts: {e}")
            return [f"Image representing {heading}" for heading in subheadings[:3]]
    
    def generate_images(self, image_prompts: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
        """Create image placeholders with prompts instead of generating actual images."""
        try:
            generated_images = {}
            
            # Create header image placeholder
            if "header_image" in image_prompts:
                header_prompt = image_prompts["header_image"]
                generated_images["header"] = {
                    "prompt": header_prompt,
                    "placeholder": f"[HEADER_IMAGE_PLACEHOLDER: {header_prompt}]",
                    "type": "header",
                    "alt_text": f"Header image for blog post"
                }
                logger.info(f"Created header image placeholder with prompt: {header_prompt[:50]}...")
            
            # Create supplemental image placeholders
            if "supplemental_images" in image_prompts:
                for i, prompt in enumerate(image_prompts["supplemental_images"]):
                    key = f"supplemental_{i+1}"
                    generated_images[key] = {
                        "prompt": prompt,
                        "placeholder": f"[SUPPLEMENTAL_IMAGE_PLACEHOLDER_{i+1}: {prompt}]",
                        "type": "supplemental",
                        "alt_text": f"Supplemental image {i+1} for blog post"
                    }
                    logger.info(f"Created supplemental image placeholder {i+1} with prompt: {prompt[:50]}...")
            
            logger.info(f"Created {len(generated_images)} image placeholders with prompts")
            return generated_images
            
        except Exception as e:
            logger.error(f"Failed to create image placeholders: {e}")
            raise
    
    def link_images_in_content(self, content: str, image_placeholders: Dict[str, Dict[str, str]]) -> str:
        """Add image placeholders to the blog post content."""
        try:
            image_info = "\n".join([
                f"- {key}: {data['prompt']}" for key, data in image_placeholders.items()
            ])
            
            task_description = f"""
            Add appropriate image placeholders to this blog post content:
            
            CONTENT:
            {content}
            
            AVAILABLE IMACE PLACEHOLDERS:
            {image_info}
            
            Please:
            - Add header image placeholder at the top of the post
            - Place supplemental image placeholders at relevant points in the content
            - Use the placeholder format: [IMAGE_PLACEHOLDER: prompt]
            - Ensure placeholders enhance the content flow
            - Add descriptive context for where images should be placed
            
            Return the content with properly placed image placeholders.
            """
            
            result = self.execute_task(task_description)
            logger.info("Added image placeholders to blog post content")
            return result.strip()
            
        except Exception as e:
            logger.error(f"Failed to link image placeholders in content: {e}")
            # Fallback: simple placeholder insertion
            return self._simple_image_placeholder_linking(content, image_placeholders)
    
    def _simple_image_placeholder_linking(self, content: str, image_placeholders: Dict[str, Dict[str, str]]) -> str:
        """Simple fallback for linking image placeholders in content."""
        try:
            # Add header image placeholder at the top
            if "header" in image_placeholders:
                header_data = image_placeholders["header"]
                content = f"{header_data['placeholder']}\n\n{content}"
            
            # Add supplemental image placeholders at the end
            for key, data in image_placeholders.items():
                if key != "header":
                    content += f"\n\n{data['placeholder']}"
            
            return content
        except Exception as e:
            logger.error(f"Failed to perform simple image placeholder linking: {e}")
            return content
    
    def _parse_image_prompts(self, response: str) -> Dict[str, Any]:
        """Parse the structured image prompts response."""
        try:
            sections = {
                "header_image": "",
                "supplemental_images": [],
                "style_notes": ""
            }
            
            current_section = None
            lines = response.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Detect section headers
                if "HEADER IMAGE:" in line.upper():
                    current_section = "header_image"
                    continue
                elif "SUPPLEMENTAL IMAGES:" in line.upper():
                    current_section = "supplemental_images"
                    continue
                elif "STYLE NOTES:" in line.upper():
                    current_section = "style_notes"
                    continue
                
                # Add content to current section
                if current_section == "header_image":
                    sections["header_image"] += line + " "
                elif current_section == "supplemental_images" and line.startswith(("1.", "2.", "3.", "-")):
                    # Extract prompt from numbered list
                    prompt = line.split(".", 1)[1].strip() if ". " in line else line[1:].strip()
                    if prompt:
                        sections["supplemental_images"].append(prompt)
                elif current_section == "style_notes":
                    sections["style_notes"] += line + " "
            
            # Clean up
            sections["header_image"] = sections["header_image"].strip()
            sections["style_notes"] = sections["style_notes"].strip()
            
            return sections
            
        except Exception as e:
            logger.error(f"Failed to parse image prompts: {e}")
            return {
                "header_image": "Professional blog header image",
                "supplemental_images": ["Supplemental image 1", "Supplemental image 2"],
                "style_notes": "Professional and engaging style"
            }
    
    def _extract_image_prompts(self, response: str) -> List[str]:
        """Extract individual image prompts from response."""
        try:
            prompts = []
            lines = response.split('\n')
            
            for line in lines:
                line = line.strip()
                if line and (line.startswith(("1.", "2.", "3.", "-")) or len(line) > 20):
                    # Clean up the prompt
                    if ". " in line:
                        prompt = line.split(". ", 1)[1]
                    elif line.startswith("- "):
                        prompt = line[2:]
                    else:
                        prompt = line
                    
                    if prompt and len(prompt) > 10:
                        prompts.append(prompt)
            
            return prompts
        except Exception as e:
            logger.error(f"Failed to extract image prompts: {e}")
            return []
    
    def _simple_image_linking(self, content: str, image_paths: Dict[str, str]) -> str:
        """Simple fallback for linking images in content."""
        try:
            # Add header image at the top
            if "header" in image_paths:
                content = f"![Blog post header]({image_paths['header']})\n\n{content}"
            
            # Add supplemental images at the end
            for key, path in image_paths.items():
                if key != "header":
                    content += f"\n\n![Supplemental image]({path})"
            
            return content
        except Exception as e:
            logger.error(f"Failed to perform simple image linking: {e}")
            return content 