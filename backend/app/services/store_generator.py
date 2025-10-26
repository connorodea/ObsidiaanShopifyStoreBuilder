import asyncio
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json
import logging

from app.core.config import settings
from app.models.store import Store
from app.models.user import User
from app.scraper.product_scraper import ProductScraperService, ScrapedProduct
from app.ai.content_generator import AIContentGenerator, ProductInfo
from app.ai.image_enhancer import LeonardoImageEnhancer
from app.services.shopify_client import ShopifyClient

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StoreGeneratorService:
    """
    Main service that orchestrates the complete store generation process
    """
    
    def __init__(self):
        self.scraper = ProductScraperService()
        self.content_generator = AIContentGenerator()
        self.image_enhancer = LeonardoImageEnhancer()
        
        # Database session
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        self.db = SessionLocal()
    
    async def generate_complete_store(self, store_id: int, product_url: str) -> Dict:
        """
        Generate a complete Shopify store from a product URL
        
        Steps:
        1. Scrape product data
        2. Generate AI content
        3. Enhance images
        4. Create store structure
        5. Update database
        """
        try:
            store = self.db.query(Store).filter(Store.id == store_id).first()
            if not store:
                raise Exception(f"Store {store_id} not found")
            
            # Update progress
            await self._update_store_progress(store, 10, "Scraping product data...")
            
            # Step 1: Scrape product data
            logger.info(f"Scraping product from: {product_url}")
            scraped_product = await self.scraper.scrape_product(product_url)
            
            await self._update_store_progress(store, 25, "Generating AI content...")
            
            # Step 2: Convert scraped data to ProductInfo format
            product_info = ProductInfo(
                title=scraped_product.title,
                description=scraped_product.description,
                features=scraped_product.features,
                specifications=scraped_product.specifications,
                category=scraped_product.category,
                price_range=scraped_product.price
            )
            
            # Step 3: Generate AI content
            logger.info("Generating AI content...")
            generated_content = await self.content_generator.generate_complete_content(product_info)
            
            await self._update_store_progress(store, 50, "Enhancing product images...")
            
            # Step 4: Enhance images
            logger.info("Enhancing product images...")
            enhanced_images = []
            if scraped_product.images:
                enhanced_images = await self.image_enhancer.enhance_product_images(
                    scraped_product.images,
                    style=store.theme_style
                )
            
            await self._update_store_progress(store, 75, "Building store structure...")
            
            # Step 5: Create complete store data structure
            store_data = await self._build_store_structure(
                store, scraped_product, generated_content, enhanced_images
            )
            
            await self._update_store_progress(store, 90, "Finalizing store...")
            
            # Step 6: Update database with generated content
            store.ai_generated_content = store_data
            store.enhanced_images = [img.dict() for img in enhanced_images]
            store.seo_title = generated_content.seo_title
            store.seo_description = generated_content.seo_description
            store.seo_keywords = generated_content.keywords
            store.status = "completed"
            store.generation_progress = 100
            store.error_message = None
            
            self.db.commit()
            
            logger.info(f"Store generation completed for store {store_id}")
            
            return {
                "store_id": store_id,
                "status": "completed",
                "store_data": store_data,
                "enhanced_images": len(enhanced_images),
                "message": "Store generated successfully"
            }
            
        except Exception as e:
            logger.error(f"Store generation failed for store {store_id}: {str(e)}")
            
            # Update store with error
            store = self.db.query(Store).filter(Store.id == store_id).first()
            if store:
                store.status = "error"
                store.error_message = str(e)
                self.db.commit()
            
            raise e
    
    async def publish_to_shopify(self, store_id: int) -> Dict:
        """
        Publish generated store to Shopify
        """
        try:
            store = self.db.query(Store).filter(Store.id == store_id).first()
            if not store:
                raise Exception(f"Store {store_id} not found")
            
            user = self.db.query(User).filter(User.id == store.user_id).first()
            if not user:
                raise Exception("User not found")
            
            # Initialize Shopify client
            shopify_client = ShopifyClient(
                shop_domain=user.shopify_shop_domain,
                access_token=user.shopify_access_token
            )
            
            # Create product in Shopify
            product_data = store.ai_generated_content.get("product", {})
            
            shopify_product = await shopify_client.create_product({
                "title": product_data.get("title", store.store_name),
                "body_html": product_data.get("description", ""),
                "vendor": user.company or "StoreForge",
                "product_type": store.ai_generated_content.get("category", "General"),
                "tags": ", ".join(store.seo_keywords or []),
                "images": [{"src": img["enhanced_url"]} for img in store.enhanced_images if img.get("enhanced_url")]
            })
            
            # Create store pages
            await self._create_store_pages(shopify_client, store)
            
            # Update store with Shopify data
            store.shopify_store_url = f"https://{user.shopify_shop_domain}"
            store.status = "published"
            
            self.db.commit()
            
            return {
                "store_id": store_id,
                "status": "published",
                "shopify_url": store.shopify_store_url,
                "product_id": shopify_product.get("id"),
                "message": "Store published successfully"
            }
            
        except Exception as e:
            logger.error(f"Publishing failed for store {store_id}: {str(e)}")
            raise e
    
    async def _build_store_structure(
        self, 
        store: Store, 
        scraped_product: ScrapedProduct,
        generated_content,
        enhanced_images: List
    ) -> Dict:
        """
        Build complete store data structure
        """
        
        # Product data
        product_data = {
            "title": generated_content.product_title,
            "description": generated_content.product_description,
            "benefits": generated_content.product_benefits,
            "original_title": scraped_product.title,
            "original_description": scraped_product.description,
            "price": scraped_product.price,
            "features": scraped_product.features,
            "specifications": scraped_product.specifications,
            "category": scraped_product.category,
            "images": {
                "original": scraped_product.images,
                "enhanced": [img.enhanced_url for img in enhanced_images]
            }
        }
        
        # Homepage content
        homepage_data = {
            "hero": generated_content.homepage_hero,
            "featured_product": {
                "title": generated_content.product_title,
                "description": generated_content.product_description[:200] + "...",
                "image": enhanced_images[0].enhanced_url if enhanced_images else scraped_product.images[0] if scraped_product.images else None,
                "cta_text": generated_content.homepage_hero.get("cta_text", "Shop Now")
            },
            "features_section": {
                "headline": generated_content.homepage_hero.get("features_headline", "Why Choose Us"),
                "features": generated_content.product_benefits[:3]  # Top 3 benefits
            }
        }
        
        # Store pages
        pages_data = {
            "about": {
                "title": "About Us",
                "content": generated_content.about_page
            },
            "faq": {
                "title": "Frequently Asked Questions",
                "items": generated_content.faq_items
            },
            "contact": {
                "title": "Contact Us",
                "content": self._generate_contact_page_content(store)
            },
            "shipping": {
                "title": "Shipping & Returns",
                "content": self._generate_shipping_policy()
            },
            "privacy": {
                "title": "Privacy Policy",
                "content": self._generate_privacy_policy()
            }
        }
        
        # SEO data
        seo_data = {
            "title": generated_content.seo_title,
            "description": generated_content.seo_description,
            "keywords": generated_content.keywords,
            "og_image": enhanced_images[0].enhanced_url if enhanced_images else None
        }
        
        # Theme configuration
        theme_data = {
            "style": store.theme_style,
            "colors": store.brand_colors or self._generate_default_colors(store.theme_style),
            "fonts": self._get_theme_fonts(store.theme_style),
            "layout": self._get_theme_layout(store.theme_style)
        }
        
        return {
            "product": product_data,
            "homepage": homepage_data,
            "pages": pages_data,
            "seo": seo_data,
            "theme": theme_data,
            "generated_at": store.created_at.isoformat(),
            "store_name": store.store_name,
            "source_url": store.source_product_url
        }
    
    async def _create_store_pages(self, shopify_client: ShopifyClient, store: Store):
        """
        Create additional store pages in Shopify
        """
        pages_data = store.ai_generated_content.get("pages", {})
        
        for page_key, page_content in pages_data.items():
            if page_key in ["about", "faq", "contact", "shipping", "privacy"]:
                await shopify_client.create_page({
                    "title": page_content["title"],
                    "body_html": self._format_page_content(page_content),
                    "published": True
                })
    
    def _format_page_content(self, page_content: Dict) -> str:
        """
        Format page content as HTML
        """
        if "items" in page_content:  # FAQ page
            html = f"<h1>{page_content['title']}</h1>"
            for item in page_content["items"]:
                html += f"""
                <div class="faq-item">
                    <h3>{item['question']}</h3>
                    <p>{item['answer']}</p>
                </div>
                """
            return html
        else:
            return f"<h1>{page_content['title']}</h1><div>{page_content['content']}</div>"
    
    def _generate_contact_page_content(self, store: Store) -> str:
        """
        Generate contact page content
        """
        return f"""
        <h2>Get in Touch</h2>
        <p>We're here to help! Contact us with any questions about our products or services.</p>
        
        <h3>Customer Service</h3>
        <p>Email: support@{store.store_name.lower().replace(' ', '')}.com</p>
        <p>Response time: Within 24 hours</p>
        
        <h3>Business Hours</h3>
        <p>Monday - Friday: 9:00 AM - 6:00 PM EST</p>
        <p>Saturday - Sunday: 10:00 AM - 4:00 PM EST</p>
        
        <h3>Returns & Exchanges</h3>
        <p>We accept returns within 30 days of purchase. Please contact us to initiate a return.</p>
        """
    
    def _generate_shipping_policy(self) -> str:
        """
        Generate shipping policy content
        """
        return """
        <h2>Shipping Information</h2>
        
        <h3>Processing Time</h3>
        <p>All orders are processed within 1-2 business days. Orders are not shipped or delivered on weekends or holidays.</p>
        
        <h3>Shipping Rates & Delivery Estimates</h3>
        <ul>
            <li><strong>Standard Shipping:</strong> 5-7 business days - $5.99</li>
            <li><strong>Express Shipping:</strong> 2-3 business days - $12.99</li>
            <li><strong>Overnight Shipping:</strong> 1 business day - $24.99</li>
        </ul>
        
        <p><strong>Free shipping on orders over $50!</strong></p>
        
        <h3>International Shipping</h3>
        <p>We ship worldwide. International shipping rates and delivery times vary by destination.</p>
        
        <h3>Returns</h3>
        <p>We accept returns within 30 days of delivery. Items must be unused and in original packaging.</p>
        """
    
    def _generate_privacy_policy(self) -> str:
        """
        Generate privacy policy content
        """
        return """
        <h2>Privacy Policy</h2>
        
        <h3>Information We Collect</h3>
        <p>We collect information you provide directly to us, such as when you create an account, make a purchase, or contact us.</p>
        
        <h3>How We Use Your Information</h3>
        <ul>
            <li>Process and fulfill your orders</li>
            <li>Send you important updates about your order</li>
            <li>Improve our products and services</li>
            <li>Comply with legal obligations</li>
        </ul>
        
        <h3>Information Sharing</h3>
        <p>We do not sell, trade, or otherwise transfer your personal information to third parties without your consent, except as described in this policy.</p>
        
        <h3>Data Security</h3>
        <p>We implement appropriate security measures to protect your personal information against unauthorized access, alteration, disclosure, or destruction.</p>
        
        <h3>Contact Us</h3>
        <p>If you have any questions about this Privacy Policy, please contact us.</p>
        """
    
    def _generate_default_colors(self, theme_style: str) -> Dict[str, str]:
        """
        Generate default color scheme based on theme style
        """
        color_schemes = {
            "modern": {
                "primary": "#3b82f6",
                "secondary": "#64748b", 
                "accent": "#f59e0b",
                "background": "#ffffff",
                "text": "#1f2937"
            },
            "luxury": {
                "primary": "#1f2937",
                "secondary": "#d97706",
                "accent": "#92400e",
                "background": "#f9fafb",
                "text": "#111827"
            },
            "minimal": {
                "primary": "#000000",
                "secondary": "#6b7280",
                "accent": "#9ca3af",
                "background": "#ffffff",
                "text": "#374151"
            }
        }
        
        return color_schemes.get(theme_style, color_schemes["modern"])
    
    def _get_theme_fonts(self, theme_style: str) -> Dict[str, str]:
        """
        Get font configuration for theme style
        """
        font_configs = {
            "modern": {
                "primary": "Inter, sans-serif",
                "secondary": "System UI, sans-serif"
            },
            "luxury": {
                "primary": "Playfair Display, serif",
                "secondary": "Source Sans Pro, sans-serif"
            },
            "minimal": {
                "primary": "Helvetica Neue, sans-serif",
                "secondary": "Arial, sans-serif"
            }
        }
        
        return font_configs.get(theme_style, font_configs["modern"])
    
    def _get_theme_layout(self, theme_style: str) -> Dict[str, str]:
        """
        Get layout configuration for theme style
        """
        layout_configs = {
            "modern": {
                "header_style": "clean",
                "product_layout": "grid",
                "spacing": "comfortable"
            },
            "luxury": {
                "header_style": "elegant",
                "product_layout": "showcase",
                "spacing": "spacious"
            },
            "minimal": {
                "header_style": "simple",
                "product_layout": "minimal",
                "spacing": "tight"
            }
        }
        
        return layout_configs.get(theme_style, layout_configs["modern"])
    
    async def _update_store_progress(self, store: Store, progress: int, message: str):
        """
        Update store generation progress
        """
        store.generation_progress = progress
        store.error_message = message  # Using error_message field for status updates
        self.db.commit()
        logger.info(f"Store {store.id}: {progress}% - {message}")
    
    def __del__(self):
        """
        Close database session
        """
        if hasattr(self, 'db'):
            self.db.close()