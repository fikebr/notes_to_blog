"""
Base agent class for CrewAI agents.

Provides common functionality, configuration management, logging, monitoring,
and prompt template loading for all agents in the Notes to Blog application.
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional, List

from crewai import Agent, Task
from pydantic import BaseModel

from src.models.config_models import Config
from src.services import ServiceRegistry

logger = logging.getLogger(__name__)


class AgentConfig(BaseModel):
    """Configuration for individual agents."""
    
    name: str
    role: str
    goal: str
    backstory: str
    verbose: bool = True
    allow_delegation: bool = False
    max_iterations: int = 3
    memory: bool = True


class BaseAgent(ABC):
    """Base class for all CrewAI agents."""
    
    def __init__(self, config: Config, service_registry: ServiceRegistry):
        """Initialize base agent."""
        self.config = config
        self.service_registry = service_registry
        self.agent_config = self._get_agent_config()
        self.prompt_template = self._load_prompt_template()
        self.crewai_agent = self._create_crewai_agent()
        
        logger.info(f"Initialized {self.agent_config.name} agent")
    
    @abstractmethod
    def _get_agent_config(self) -> AgentConfig:
        """Get agent-specific configuration."""
        pass
    
    @abstractmethod
    def _get_prompt_template_path(self) -> Path:
        """Get path to agent's prompt template file."""
        pass
    
    def _load_prompt_template(self) -> str:
        """Load prompt template from file."""
        template_path = self._get_prompt_template_path()
        
        try:
            if template_path.exists():
                with open(template_path, 'r', encoding='utf-8') as f:
                    template = f.read().strip()
                logger.debug(f"Loaded prompt template from {template_path}")
                return template
            else:
                logger.warning(f"Prompt template not found at {template_path}, using default")
                return self._get_default_prompt_template()
        except Exception as e:
            logger.error(f"Failed to load prompt template from {template_path}: {e}")
            return self._get_default_prompt_template()
    
    @abstractmethod
    def _get_default_prompt_template(self) -> str:
        """Get default prompt template if file loading fails."""
        pass
    
    def _create_crewai_agent(self) -> Agent:
        """Create CrewAI agent instance."""
        try:
            # Use CrewAI's built-in OpenRouter support
            # Configure the LLM with OpenRouter model string from config
            from crewai import Agent
            model_name = self.config.api.openrouter_model if hasattr(self.config.api, 'openrouter_model') else "openai/gpt-4"
            agent = Agent(
                role=self.agent_config.role,
                goal=self.agent_config.goal,
                backstory=self.agent_config.backstory,
                verbose=self.agent_config.verbose,
                allow_delegation=self.agent_config.allow_delegation,
                max_iter=self.agent_config.max_iterations,
                memory=self.agent_config.memory,
                llm=model_name  # Configurable model name
            )
            
            logger.info(f"Created CrewAI agent: {self.agent_config.name} using model: {model_name}")
            return agent
            
        except Exception as e:
            logger.error(f"Failed to create CrewAI agent {self.agent_config.name}: {e}")
            raise
    
    def get_agent(self) -> Agent:
        """Get the CrewAI agent instance."""
        return self.crewai_agent
    
    def render_prompt(self, **kwargs) -> str:
        """Render prompt template with provided variables."""
        try:
            return self.prompt_template.format(**kwargs)
        except KeyError as e:
            logger.error(f"Missing required variable in prompt template: {e}")
            return self.prompt_template
        except Exception as e:
            logger.error(f"Failed to render prompt template: {e}")
            return self.prompt_template
    
    def execute_task(self, task_description: str, **kwargs) -> str:
        """Execute a task using the agent."""
        try:
            # Render the prompt with task description and additional kwargs
            prompt = self.render_prompt(
                task_description=task_description,
                **kwargs
            )
            
            logger.info(f"Executing task with {self.agent_config.name}")
            logger.debug(f"Task prompt: {prompt[:200]}...")
            
            # Create a proper CrewAI Task object
            task = Task(
                description=prompt,
                agent=self.crewai_agent,
                expected_output="Detailed response based on the task description"
            )
            
            # Execute the task using CrewAI agent
            result = self.crewai_agent.execute_task(task)
            
            logger.info(f"Task completed by {self.agent_config.name}")
            return result
            
        except Exception as e:
            logger.error(f"Task execution failed for {self.agent_config.name}: {e}")
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check of the agent."""
        try:
            return {
                "name": self.agent_config.name,
                "status": "healthy",
                "crewai_agent_created": self.crewai_agent is not None,
                "prompt_template_loaded": bool(self.prompt_template),
                "timestamp": "2025-01-27T00:00:00Z"  # Placeholder
            }
        except Exception as e:
            return {
                "name": self.agent_config.name,
                "status": "unhealthy",
                "error": str(e),
                "timestamp": "2025-01-27T00:00:00Z"  # Placeholder
            } 