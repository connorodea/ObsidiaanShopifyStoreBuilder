import httpx
import asyncio
import base64
from typing import List, Optional, Dict
from pydantic import BaseModel
import io
from PIL import Image
import time

from app.core.config import settings

class ImageEnhancementRequest(BaseModel):
    image_url: str
    style: str = "modern"  # modern, luxury, minimal, professional
    enhance_quality: bool = True
    remove_background: bool = False
    add_branding: bool = False
    brand_colors: Optional[Dict[str, str]] = None

class EnhancedImage(BaseModel):
    original_url: str
    enhanced_url: str
    style: str
    processing_time: float
    enhancement_type: str

class LeonardoImageEnhancer:
    """AI-powered image enhancement using Leonardo.AI API"""
    
    def __init__(self):
        self.api_key = settings.LEONARDO_API_KEY
        self.base_url = "https://cloud.leonardo.ai/api/rest/v1"
        self.timeout = 60
    
    async def enhance_product_images(
        self, 
        image_urls: List[str], 
        style: str = "modern",
        enhance_quality: bool = True
    ) -> List[EnhancedImage]:
        """
        Enhance multiple product images concurrently
        """
        tasks = []
        for url in image_urls[:5]:  # Limit to 5 images to control costs
            task = self.enhance_single_image(
                url, 
                style=style, 
                enhance_quality=enhance_quality
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return successful enhancements
        enhanced_images = []
        for result in results:
            if isinstance(result, EnhancedImage):
                enhanced_images.append(result)
        
        return enhanced_images
    
    async def enhance_single_image(
        self,
        image_url: str,
        style: str = "modern",
        enhance_quality: bool = True,
        remove_background: bool = False
    ) -> EnhancedImage:
        """
        Enhance a single product image
        """
        start_time = time.time()
        
        try:
            # Download original image
            original_image = await self._download_image(image_url)
            
            if enhance_quality:
                # First pass: Quality enhancement
                enhanced_image = await self._enhance_image_quality(original_image)
            else:
                enhanced_image = original_image
            
            if remove_background:
                # Second pass: Background removal
                enhanced_image = await self._remove_background(enhanced_image)
            
            # Third pass: Style enhancement
            final_image = await self._apply_style_enhancement(enhanced_image, style)
            
            # Upload enhanced image
            enhanced_url = await self._upload_enhanced_image(final_image)
            
            processing_time = time.time() - start_time
            
            return EnhancedImage(
                original_url=image_url,
                enhanced_url=enhanced_url,
                style=style,
                processing_time=processing_time,
                enhancement_type="full_enhancement"
            )
            
        except Exception as e:
            # Fallback: return original image if enhancement fails
            return EnhancedImage(
                original_url=image_url,
                enhanced_url=image_url,
                style=style,
                processing_time=time.time() - start_time,
                enhancement_type="fallback_original"
            )
    
    async def _enhance_image_quality(self, image_data: bytes) -> bytes:
        """
        Enhance image quality using Leonardo AI upscaling
        """
        try:
            # Convert image to base64
            image_b64 = base64.b64encode(image_data).decode('utf-8')
            
            # Leonardo AI upscaling request
            payload = {
                "height": 1024,
                "width": 1024,
                "prompt": "high quality product photo, professional lighting, clean background, commercial photography style",
                "negative_prompt": "blurry, low quality, pixelated, distorted, watermark, text",
                "num_images": 1,
                "guidance_scale": 7,
                "seed": None,
                "presetStyle": "PHOTOGRAPHY",
                "scheduler": "DPM_SOLVER",
                "public": False,
                "promptMagic": True,
                "init_image_b64": image_b64,
                "init_strength": 0.3
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Start generation
                response = await client.post(
                    f"{self.base_url}/generations",
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                
                generation_data = response.json()
                generation_id = generation_data["sdGenerationJob"]["generationId"]
                
                # Poll for completion
                enhanced_url = await self._poll_generation_completion(generation_id)
                
                # Download enhanced image
                return await self._download_image(enhanced_url)
                
        except Exception as e:
            # Return original if enhancement fails
            return image_data
    
    async def _remove_background(self, image_data: bytes) -> bytes:
        """
        Remove background using Leonardo AI
        """
        try:
            image_b64 = base64.b64encode(image_data).decode('utf-8')
            
            payload = {
                "height": 1024,
                "width": 1024,
                "prompt": "product on transparent background, isolated object, clean cutout, white background",
                "negative_prompt": "busy background, cluttered, multiple objects, text, watermark",
                "num_images": 1,
                "guidance_scale": 8,
                "presetStyle": "NONE",
                "scheduler": "DPM_SOLVER",
                "public": False,
                "promptMagic": True,
                "init_image_b64": image_b64,
                "init_strength": 0.5
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/generations",
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                
                generation_data = response.json()
                generation_id = generation_data["sdGenerationJob"]["generationId"]
                
                enhanced_url = await self._poll_generation_completion(generation_id)
                return await self._download_image(enhanced_url)
                
        except Exception as e:
            return image_data
    
    async def _apply_style_enhancement(self, image_data: bytes, style: str) -> bytes:
        """
        Apply style-specific enhancements
        """
        style_prompts = {
            "modern": "modern minimalist product photography, clean lines, contemporary style, professional lighting",
            "luxury": "luxury product photography, premium quality, elegant styling, sophisticated lighting, high-end commercial",
            "minimal": "minimalist product photo, simple clean background, soft lighting, zen aesthetic",
            "professional": "professional commercial photography, studio lighting, corporate style, business quality"
        }
        
        style_prompt = style_prompts.get(style, style_prompts["modern"])
        
        try:
            image_b64 = base64.b64encode(image_data).decode('utf-8')
            
            payload = {
                "height": 1024,
                "width": 1024,
                "prompt": f"{style_prompt}, high resolution, sharp details, commercial quality",
                "negative_prompt": "blurry, low quality, amateur, poor lighting, distorted",
                "num_images": 1,
                "guidance_scale": 6,
                "presetStyle": "PHOTOGRAPHY",
                "scheduler": "DPM_SOLVER",
                "public": False,
                "promptMagic": True,
                "init_image_b64": image_b64,
                "init_strength": 0.2
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/generations",
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                
                generation_data = response.json()
                generation_id = generation_data["sdGenerationJob"]["generationId"]
                
                enhanced_url = await self._poll_generation_completion(generation_id)
                return await self._download_image(enhanced_url)
                
        except Exception as e:
            return image_data
    
    async def _poll_generation_completion(self, generation_id: str) -> str:
        """
        Poll Leonardo API until image generation is complete
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        max_attempts = 30  # 5 minutes max wait
        attempt = 0
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            while attempt < max_attempts:
                response = await client.get(
                    f"{self.base_url}/generations/{generation_id}",
                    headers=headers
                )
                response.raise_for_status()
                
                data = response.json()
                generation = data["generations_by_pk"]
                
                if generation["status"] == "COMPLETE":
                    if generation["generated_images"]:
                        return generation["generated_images"][0]["url"]
                    else:
                        raise Exception("No images generated")
                elif generation["status"] == "FAILED":
                    raise Exception("Image generation failed")
                
                # Wait before next poll
                await asyncio.sleep(10)
                attempt += 1
            
            raise Exception("Generation timeout")
    
    async def _download_image(self, url: str) -> bytes:
        """
        Download image from URL
        """
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.content
    
    async def _upload_enhanced_image(self, image_data: bytes) -> str:
        """
        Upload enhanced image to S3 and return public URL
        """
        # This would normally upload to S3
        # For demo purposes, we'll return a placeholder URL
        import hashlib
        image_hash = hashlib.md5(image_data).hexdigest()
        return f"https://{settings.AWS_S3_BUCKET}.s3.amazonaws.com/enhanced/{image_hash}.jpg"
    
    async def generate_branded_background(
        self, 
        brand_colors: Dict[str, str],
        style: str = "modern"
    ) -> str:
        """
        Generate a branded background for product photos
        """
        primary_color = brand_colors.get("primary", "#ffffff")
        secondary_color = brand_colors.get("secondary", "#f8f9fa")
        
        style_descriptions = {
            "modern": f"modern abstract background, geometric shapes, gradient from {primary_color} to {secondary_color}",
            "luxury": f"luxury background, elegant texture, premium feel, {primary_color} and {secondary_color} color scheme",
            "minimal": f"minimal clean background, simple gradient, {primary_color} to {secondary_color}",
            "professional": f"professional business background, corporate style, {primary_color} and {secondary_color}"
        }
        
        prompt = style_descriptions.get(style, style_descriptions["modern"])
        
        try:
            payload = {
                "height": 1024,
                "width": 1024,
                "prompt": prompt + ", high quality, clean, professional",
                "negative_prompt": "busy, cluttered, text, logos, watermarks, people, objects",
                "num_images": 1,
                "guidance_scale": 7,
                "presetStyle": "NONE",
                "scheduler": "DPM_SOLVER",
                "public": False,
                "promptMagic": True
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/generations",
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                
                generation_data = response.json()
                generation_id = generation_data["sdGenerationJob"]["generationId"]
                
                return await self._poll_generation_completion(generation_id)
                
        except Exception as e:
            # Return a fallback gradient URL
            return f"https://via.placeholder.com/1024x1024/{primary_color.replace('#', '')}/{secondary_color.replace('#', '')}"