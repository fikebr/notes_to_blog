"""
Replicate.com service for image generation.

This module provides functionality for interacting with Replicate.com API,
including image generation, format validation, processing, and storage.
"""

import logging
import time
import asyncio
import aiohttp
import aiofiles
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
import hashlib

import httpx
from pydantic import BaseModel, Field, field_validator

from models import Config

logger = logging.getLogger(__name__)


class ReplicatePrediction(BaseModel):
    """Replicate prediction model."""
    
    id: str = Field(..., description="Prediction ID")
    version: str = Field(..., description="Model version")
    status: str = Field(..., description="Prediction status")
    input: Dict[str, Any] = Field(..., description="Input parameters")
    output: Optional[Union[str, List[str]]] = Field(default=None, description="Generated output")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    created_at: str = Field(..., description="Creation timestamp")
    started_at: Optional[str] = Field(default=None, description="Start timestamp")
    completed_at: Optional[str] = Field(default=None, description="Completion timestamp")


class ImageGenerationRequest(BaseModel):
    """Image generation request model."""
    
    prompt: str = Field(..., min_length=1, max_length=1000, description="Image generation prompt")
    width: int = Field(default=1024, ge=256, le=2048, description="Image width")
    height: int = Field(default=1024, ge=256, le=2048, description="Image height")
    num_outputs: int = Field(default=1, ge=1, le=4, description="Number of images to generate")
    guidance_scale: float = Field(default=7.5, ge=1.0, le=20.0, description="Guidance scale")
    num_inference_steps: int = Field(default=50, ge=10, le=100, description="Inference steps")
    seed: Optional[int] = Field(default=None, ge=0, le=2**32-1, description="Random seed")
    negative_prompt: Optional[str] = Field(default=None, max_length=1000, description="Negative prompt")
    
    @field_validator('width', 'height', mode='after')
    def validate_dimensions(cls, v):
        """Validate image dimensions are multiples of 8."""
        if v % 8 != 0:
            raise ValueError("Image dimensions must be multiples of 8")
        return v


class ImageGenerationResult(BaseModel):
    """Image generation result model."""
    
    success: bool = Field(..., description="Whether generation was successful")
    image_urls: List[str] = Field(default_factory=list, description="Generated image URLs")
    prediction_id: Optional[str] = Field(default=None, description="Replicate prediction ID")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    generation_time: Optional[float] = Field(default=None, description="Generation time in seconds")
    model_used: str = Field(..., description="Model used for generation")


class ImageProcessor:
    """Image processing utilities."""
    
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.webp'}
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    @staticmethod
    def validate_image_url(url: str) -> bool:
        """Validate image URL format."""
        try:
            parsed = urlparse(url)
            return parsed.scheme in {'http', 'https'} and parsed.netloc
        except Exception:
            return False
    
    @staticmethod
    def get_file_extension(url: str) -> str:
        """Extract file extension from URL."""
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        # Check for common image extensions
        for ext in ImageProcessor.SUPPORTED_FORMATS:
            if path.endswith(ext):
                return ext
        
        # Default to .png if no extension found
        return '.png'
    
    @staticmethod
    def generate_filename(prompt: str, index: int = 0) -> str:
        """Generate filename from prompt."""
        # Create a hash of the prompt for consistent naming
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"image_{prompt_hash}_{timestamp}_{index}"
    
    @staticmethod
    async def download_image(url: str, save_path: Path) -> bool:
        """Download image from URL."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        content = await response.read()
                        
                        # Validate file size
                        if len(content) > ImageProcessor.MAX_FILE_SIZE:
                            logger.warning(f"Image too large: {len(content)} bytes")
                            return False
                        
                        # Save file
                        async with aiofiles.open(save_path, 'wb') as f:
                            await f.write(content)
                        
                        logger.info(f"Downloaded image: {save_path}")
                        return True
                    else:
                        logger.error(f"Failed to download image: HTTP {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error downloading image: {e}")
            return False


class ReplicateService:
    """Service for interacting with Replicate.com API."""
    
    def __init__(self, config: Config):
        """Initialize Replicate service."""
        self.config = config
        self.api_token = config.api.replicate_api_token
        self.base_url = "https://api.replicate.com/v1"
        self.model_id = config.image.image_model
        
        # HTTP client with timeout
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(
                connect=10.0,
                read=300.0,  # Longer timeout for image generation
                write=10.0,
                pool=30.0
            ),
            headers={
                "Authorization": f"Token {self.api_token}",
                "Content-Type": "application/json",
                "User-Agent": f"NotesToBlog/{config.app.app_version}"
            }
        )
        
        self._validate_configuration()
    
    def _validate_configuration(self) -> None:
        """Validate service configuration."""
        if not self.api_token or self.api_token == "your_replicate_api_token_here":
            raise ValueError("Replicate API token not configured")
        
        if not self.model_id:
            raise ValueError("Replicate model ID not configured")
        
        logger.info(f"Replicate service initialized with model: {self.model_id}")
    
    async def generate_image(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        num_outputs: int = 1,
        **kwargs
    ) -> ImageGenerationResult:
        """Generate image using Replicate API."""
        
        try:
            start_time = time.time()
            
            # Prepare request
            request_data = ImageGenerationRequest(
                prompt=prompt,
                width=width,
                height=height,
                num_outputs=num_outputs,
                **kwargs
            )
            
            # Create prediction
            prediction = await self._create_prediction(request_data)
            
            if not prediction:
                return ImageGenerationResult(
                    success=False,
                    error="Failed to create prediction",
                    model_used=self.model_id
                )
            
            # Wait for completion
            result = await self._wait_for_completion(prediction.id)
            
            generation_time = time.time() - start_time
            
            if result["success"]:
                return ImageGenerationResult(
                    success=True,
                    image_urls=result["image_urls"],
                    prediction_id=prediction.id,
                    generation_time=generation_time,
                    model_used=self.model_id
                )
            else:
                return ImageGenerationResult(
                    success=False,
                    error=result["error"],
                    prediction_id=prediction.id,
                    generation_time=generation_time,
                    model_used=self.model_id
                )
                
        except Exception as e:
            logger.error(f"Failed to generate image: {e}")
            return ImageGenerationResult(
                success=False,
                error=str(e),
                model_used=self.model_id
            )
    
    async def _create_prediction(self, request_data: ImageGenerationRequest) -> Optional[ReplicatePrediction]:
        """Create a new prediction."""
        
        try:
            response = await self.client.post(
                f"{self.base_url}/predictions",
                json={
                    "version": self.model_id,
                    "input": request_data.model_dump()
                }
            )
            
            response.raise_for_status()
            data = response.json()
            
            prediction = ReplicatePrediction(**data)
            logger.info(f"Created prediction: {prediction.id}")
            
            return prediction
            
        except Exception as e:
            logger.error(f"Failed to create prediction: {e}")
            return None
    
    async def _wait_for_completion(self, prediction_id: str, max_wait: int = 300) -> Dict[str, Any]:
        """Wait for prediction completion."""
        
        start_time = time.time()
        poll_interval = 2  # Start with 2 seconds
        
        while time.time() - start_time < max_wait:
            try:
                response = await self.client.get(f"{self.base_url}/predictions/{prediction_id}")
                response.raise_for_status()
                
                data = response.json()
                prediction = ReplicatePrediction(**data)
                
                if prediction.status == "succeeded":
                    # Extract image URLs
                    if isinstance(prediction.output, list):
                        image_urls = prediction.output
                    elif isinstance(prediction.output, str):
                        image_urls = [prediction.output]
                    else:
                        image_urls = []
                    
                    logger.info(f"Prediction completed: {prediction_id}")
                    return {
                        "success": True,
                        "image_urls": image_urls
                    }
                
                elif prediction.status == "failed":
                    logger.error(f"Prediction failed: {prediction.error}")
                    return {
                        "success": False,
                        "error": prediction.error or "Unknown error"
                    }
                
                elif prediction.status in ["starting", "processing"]:
                    logger.debug(f"Prediction {prediction.status}: {prediction_id}")
                    await asyncio.sleep(poll_interval)
                    poll_interval = min(poll_interval * 1.5, 10)  # Exponential backoff
                
                else:
                    logger.warning(f"Unknown prediction status: {prediction.status}")
                    await asyncio.sleep(poll_interval)
                    
            except Exception as e:
                logger.error(f"Error checking prediction status: {e}")
                await asyncio.sleep(poll_interval)
        
        return {
            "success": False,
            "error": f"Prediction timed out after {max_wait} seconds"
        }
    
    async def download_and_save_images(
        self,
        image_urls: List[str],
        save_directory: Path,
        prompt: str
    ) -> List[Path]:
        """Download and save images to local directory."""
        
        saved_paths = []
        
        for i, url in enumerate(image_urls):
            try:
                # Validate URL
                if not ImageProcessor.validate_image_url(url):
                    logger.warning(f"Invalid image URL: {url}")
                    continue
                
                # Generate filename
                filename = ImageProcessor.generate_filename(prompt, i)
                extension = ImageProcessor.get_file_extension(url)
                file_path = save_directory / f"{filename}{extension}"
                
                # Download image
                if await ImageProcessor.download_image(url, file_path):
                    saved_paths.append(file_path)
                else:
                    logger.error(f"Failed to download image: {url}")
                    
            except Exception as e:
                logger.error(f"Error processing image {url}: {e}")
        
        return saved_paths
    
    async def generate_and_save_image(
        self,
        prompt: str,
        save_directory: Path,
        **kwargs
    ) -> Tuple[bool, List[Path], Optional[str]]:
        """Generate image and save to local directory."""
        
        # Generate image
        result = await self.generate_image(prompt, **kwargs)
        
        if not result.success:
            return False, [], result.error
        
        # Download and save images
        saved_paths = await self.download_and_save_images(
            result.image_urls,
            save_directory,
            prompt
        )
        
        if not saved_paths:
            return False, [], "Failed to download any images"
        
        logger.info(f"Generated and saved {len(saved_paths)} images")
        return True, saved_paths, None
    
    async def get_prediction_status(self, prediction_id: str) -> Optional[ReplicatePrediction]:
        """Get prediction status."""
        
        try:
            response = await self.client.get(f"{self.base_url}/predictions/{prediction_id}")
            response.raise_for_status()
            
            data = response.json()
            return ReplicatePrediction(**data)
            
        except Exception as e:
            logger.error(f"Failed to get prediction status: {e}")
            return None
    
    async def cancel_prediction(self, prediction_id: str) -> bool:
        """Cancel a running prediction."""
        
        try:
            response = await self.client.post(f"{self.base_url}/predictions/{prediction_id}/cancel")
            response.raise_for_status()
            
            logger.info(f"Cancelled prediction: {prediction_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel prediction: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of the service."""
        
        try:
            start_time = time.time()
            
            # Test with a simple prompt
            result = await self.generate_image(
                prompt="A simple test image",
                width=512,
                height=512,
                num_outputs=1
            )
            
            response_time = time.time() - start_time
            
            return {
                "status": "healthy" if result.success else "unhealthy",
                "response_time": response_time,
                "error": result.error,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def close(self) -> None:
        """Close the service and cleanup resources."""
        
        await self.client.aclose()
        logger.info("Replicate service closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        asyncio.create_task(self.close()) 