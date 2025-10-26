import openai
from typing import Dict, List, Optional
from pydantic import BaseModel
import json
import asyncio
from app.core.config import settings

openai.api_key = settings.OPENAI_API_KEY

class ProductInfo(BaseModel):
    title: str
    description: str
    features: List[str]
    specifications: Dict[str, str]
    category: str
    price_range: Optional[str] = None

class GeneratedContent(BaseModel):
    product_title: str
    product_description: str
    seo_title: str
    seo_description: str
    homepage_hero: Dict[str, str]
    about_page: str
    faq_items: List[Dict[str, str]]
    product_benefits: List[str]
    keywords: List[str]

class AIContentGenerator:
    """AI-powered content generation using OpenAI GPT-4"""
    
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def generate_complete_content(self, product_info: ProductInfo) -> GeneratedContent:
        """Generate all content for a store from product information"""
        
        # Run all content generation tasks concurrently
        tasks = [
            self.generate_product_copy(product_info),
            self.generate_seo_content(product_info),
            self.generate_homepage_content(product_info),
            self.generate_about_page(product_info),
            self.generate_faq_content(product_info),
            self.generate_keywords(product_info)
        ]
        
        results = await asyncio.gather(*tasks)
        
        return GeneratedContent(
            product_title=results[0]["title"],
            product_description=results[0]["description"],
            seo_title=results[1]["title"],
            seo_description=results[1]["description"],
            homepage_hero=results[2],
            about_page=results[3],
            faq_items=results[4],
            product_benefits=results[0]["benefits"],
            keywords=results[5]
        )
    
    async def generate_product_copy(self, product_info: ProductInfo) -> Dict:
        """Generate enhanced product title and description"""
        
        prompt = f"""
        You are an expert e-commerce copywriter. Rewrite this product information to be highly persuasive, 
        SEO-optimized, and conversion-driven for a Shopify store.

        Original Product Info:
        Title: {product_info.title}
        Description: {product_info.description}
        Features: {', '.join(product_info.features)}
        Category: {product_info.category}

        Generate:
        1. A compelling product title (max 60 characters)
        2. A persuasive product description (200-300 words)
        3. 5 key product benefits (bullet points)

        Focus on:
        - Benefits over features
        - Emotional triggers
        - Social proof language
        - Clear value proposition
        - SEO keywords

        Return as JSON with keys: title, description, benefits
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=800
        )
        
        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            content = response.choices[0].message.content
            return {
                "title": product_info.title,
                "description": content[:300],
                "benefits": product_info.features[:5]
            }
    
    async def generate_seo_content(self, product_info: ProductInfo) -> Dict:
        """Generate SEO title and meta description"""
        
        prompt = f"""
        Create SEO-optimized title and meta description for this product:

        Product: {product_info.title}
        Category: {product_info.category}
        Description: {product_info.description[:200]}

        Requirements:
        - SEO Title: 50-60 characters, include main keyword
        - Meta Description: 150-160 characters, compelling and informative
        - Focus on search intent and conversion

        Return as JSON with keys: title, description
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=200
        )
        
        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            return {
                "title": f"{product_info.title} - Best Quality Online Store",
                "description": f"Shop {product_info.title} with fast shipping and great prices. Premium quality guaranteed."
            }
    
    async def generate_homepage_content(self, product_info: ProductInfo) -> Dict:
        """Generate homepage hero section content"""
        
        prompt = f"""
        Create compelling homepage hero content for an online store selling: {product_info.title}

        Generate:
        1. Hero headline (8-12 words, powerful and attention-grabbing)
        2. Subheadline (15-25 words, explain the value proposition)
        3. Call-to-action button text (2-4 words)
        4. Secondary headline for features section

        Make it conversion-focused and professional.

        Return as JSON with keys: headline, subheadline, cta_text, features_headline
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=300
        )
        
        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            return {
                "headline": f"Premium {product_info.category} Collection",
                "subheadline": f"Discover high-quality {product_info.title} with fast shipping worldwide",
                "cta_text": "Shop Now",
                "features_headline": "Why Choose Us"
            }
    
    async def generate_about_page(self, product_info: ProductInfo) -> str:
        """Generate About Us page content"""
        
        prompt = f"""
        Write a compelling About Us page for an online store specializing in {product_info.category}.
        
        Include:
        - Brief company story (authentic but generic)
        - Mission and values
        - Quality commitment
        - Customer focus
        
        Keep it 150-200 words, professional yet friendly tone.
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=400
        )
        
        return response.choices[0].message.content
    
    async def generate_faq_content(self, product_info: ProductInfo) -> List[Dict[str, str]]:
        """Generate FAQ items relevant to the product"""
        
        prompt = f"""
        Create 5 relevant FAQ items for a store selling {product_info.title} in the {product_info.category} category.

        Focus on common customer concerns:
        - Shipping and delivery
        - Product quality
        - Returns/exchanges
        - Sizing/compatibility
        - Warranty/support

        Return as JSON array with objects containing 'question' and 'answer' keys.
        Keep answers helpful but concise (2-3 sentences each).
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=600
        )
        
        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            # Fallback FAQs
            return [
                {
                    "question": "What is your shipping policy?",
                    "answer": "We offer free shipping on orders over $50. Standard delivery takes 3-7 business days."
                },
                {
                    "question": "What is your return policy?",
                    "answer": "We accept returns within 30 days of delivery for a full refund. Items must be in original condition."
                },
                {
                    "question": "Is this product authentic?",
                    "answer": "Yes, all our products are 100% authentic and come with a quality guarantee."
                }
            ]
    
    async def generate_keywords(self, product_info: ProductInfo) -> List[str]:
        """Generate SEO keywords for the product"""
        
        prompt = f"""
        Generate 10-15 relevant SEO keywords for this product:
        
        Product: {product_info.title}
        Category: {product_info.category}
        Features: {', '.join(product_info.features[:5])}
        
        Include:
        - Main product keywords
        - Long-tail keywords
        - Category-related terms
        - Commercial intent keywords
        
        Return as JSON array of strings.
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=300
        )
        
        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            # Fallback keywords
            return [
                product_info.title.lower(),
                f"best {product_info.category}",
                f"buy {product_info.title}",
                f"{product_info.category} online",
                f"premium {product_info.category}"
            ]
    
    async def optimize_content_for_conversion(self, content: str, goal: str = "purchase") -> str:
        """Optimize existing content for better conversion rates"""
        
        prompt = f"""
        Optimize this e-commerce content for higher conversion rates:
        
        Original Content:
        {content}
        
        Goal: Increase {goal} conversion
        
        Improvements to make:
        - Add urgency/scarcity elements
        - Strengthen value propositions
        - Include social proof language
        - Improve call-to-action language
        - Enhance emotional appeal
        
        Return the optimized version.
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=500
        )
        
        return response.choices[0].message.content