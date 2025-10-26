import asyncio
import aiohttp
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse
import re
import json
from pydantic import BaseModel

class ScrapedProduct(BaseModel):
    title: str
    description: str
    price: Optional[str] = None
    images: List[str] = []
    features: List[str] = []
    specifications: Dict[str, str] = {}
    category: str = "Unknown"
    brand: Optional[str] = None
    rating: Optional[float] = None
    reviews_count: Optional[int] = None

class ProductScraperService:
    """Universal product scraper for multiple e-commerce platforms"""
    
    def __init__(self):
        self.timeout = 30
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    async def scrape_product(self, url: str) -> ScrapedProduct:
        """Main method to scrape product from any supported platform"""
        
        domain = urlparse(url).netloc.lower()
        
        if "aliexpress.com" in domain:
            return await self._scrape_aliexpress(url)
        elif "amazon.com" in domain:
            return await self._scrape_amazon(url)
        elif "ebay.com" in domain:
            return await self._scrape_ebay(url)
        elif "bestbuy.com" in domain:
            return await self._scrape_bestbuy(url)
        else:
            return await self._scrape_generic(url)
    
    async def _scrape_aliexpress(self, url: str) -> ScrapedProduct:
        """Scrape AliExpress product page"""
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                await page.goto(url, timeout=self.timeout * 1000)
                await page.wait_for_load_state("networkidle")
                
                # Extract product data
                title = await self._get_text(page, 'h1[data-pl="product-title"]', 'h1')
                
                # Description from multiple possible selectors
                description_selectors = [
                    '[data-pl="product-description"]',
                    '.product-description',
                    '.product-overview'
                ]
                description = await self._get_text_from_selectors(page, description_selectors)
                
                # Price
                price_selectors = [
                    '.product-price-current',
                    '.price-current',
                    '[data-pl="product-price"]'
                ]
                price = await self._get_text_from_selectors(page, price_selectors)
                
                # Images
                images = await self._get_images(page, [
                    '.images-view-item img',
                    '.product-image img'
                ])
                
                # Features from product details
                features = await self._extract_features(page, [
                    '.product-property li',
                    '.product-feature li'
                ])
                
                await browser.close()
                
                return ScrapedProduct(
                    title=title or "Unknown Product",
                    description=description or "",
                    price=price,
                    images=images,
                    features=features,
                    category="Electronics"  # Default for AliExpress
                )
                
            except Exception as e:
                await browser.close()
                raise Exception(f"Failed to scrape AliExpress: {str(e)}")
    
    async def _scrape_amazon(self, url: str) -> ScrapedProduct:
        """Scrape Amazon product page"""
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Set user agent to avoid detection
            await page.set_extra_http_headers({
                'User-Agent': self.user_agent
            })
            
            try:
                await page.goto(url, timeout=self.timeout * 1000)
                await page.wait_for_load_state("networkidle")
                
                # Title
                title = await self._get_text(page, '#productTitle', 'h1')
                
                # Description
                description_selectors = [
                    '#feature-bullets ul',
                    '#productDescription',
                    '[data-feature-name="productDescription"]'
                ]
                description = await self._get_text_from_selectors(page, description_selectors)
                
                # Price
                price_selectors = [
                    '.a-price-whole',
                    '#priceblock_dealprice',
                    '#priceblock_ourprice'
                ]
                price = await self._get_text_from_selectors(page, price_selectors)
                
                # Images
                images = await self._get_images(page, [
                    '#landingImage',
                    '.image.item img'
                ])
                
                # Features
                features = await self._extract_features(page, [
                    '#feature-bullets li span',
                    '#productDetails_detailBullets_sections1 tr'
                ])
                
                await browser.close()
                
                return ScrapedProduct(
                    title=title or "Unknown Product",
                    description=description or "",
                    price=price,
                    images=images,
                    features=features,
                    category="General"
                )
                
            except Exception as e:
                await browser.close()
                raise Exception(f"Failed to scrape Amazon: {str(e)}")
    
    async def _scrape_ebay(self, url: str) -> ScrapedProduct:
        """Scrape eBay product page"""
        
        async with aiohttp.ClientSession() as session:
            headers = {'User-Agent': self.user_agent}
            
            try:
                async with session.get(url, headers=headers, timeout=self.timeout) as response:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Title
                    title_el = soup.find('h1', {'id': 'x-title-label-lbl'}) or soup.find('h1')
                    title = title_el.get_text().strip() if title_el else "Unknown Product"
                    
                    # Description
                    desc_el = soup.find('div', {'id': 'desc_div'}) or soup.find('div', class_='product-description')
                    description = desc_el.get_text().strip() if desc_el else ""
                    
                    # Price
                    price_el = soup.find('span', class_='notranslate') or soup.find('span', {'id': 'prcIsum'})
                    price = price_el.get_text().strip() if price_el else None
                    
                    # Images
                    images = []
                    img_elements = soup.find_all('img', {'id': 'icImg'}) or soup.find_all('img', class_='img')
                    for img in img_elements[:5]:
                        src = img.get('src') or img.get('data-src')
                        if src:
                            images.append(urljoin(url, src))
                    
                    return ScrapedProduct(
                        title=title,
                        description=description,
                        price=price,
                        images=images,
                        features=[],
                        category="General"
                    )
                    
            except Exception as e:
                raise Exception(f"Failed to scrape eBay: {str(e)}")
    
    async def _scrape_bestbuy(self, url: str) -> ScrapedProduct:
        """Scrape Best Buy product page"""
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                await page.goto(url, timeout=self.timeout * 1000)
                await page.wait_for_load_state("networkidle")
                
                # Title
                title = await self._get_text(page, '.sku-title h1', 'h1')
                
                # Description
                description = await self._get_text(page, '.product-data-value', '.description')
                
                # Price
                price = await self._get_text(page, '.pricing-price__range', '.price')
                
                # Images
                images = await self._get_images(page, ['.primary-image img', '.carousel-image img'])
                
                await browser.close()
                
                return ScrapedProduct(
                    title=title or "Unknown Product",
                    description=description or "",
                    price=price,
                    images=images,
                    features=[],
                    category="Electronics"
                )
                
            except Exception as e:
                await browser.close()
                raise Exception(f"Failed to scrape Best Buy: {str(e)}")
    
    async def _scrape_generic(self, url: str) -> ScrapedProduct:
        """Fallback scraper for unknown sites"""
        
        async with aiohttp.ClientSession() as session:
            headers = {'User-Agent': self.user_agent}
            
            try:
                async with session.get(url, headers=headers, timeout=self.timeout) as response:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Try to find title
                    title = self._find_title(soup)
                    
                    # Try to find description
                    description = self._find_description(soup)
                    
                    # Try to find images
                    images = self._find_images(soup, url)
                    
                    return ScrapedProduct(
                        title=title,
                        description=description,
                        images=images,
                        features=[],
                        category="General"
                    )
                    
            except Exception as e:
                raise Exception(f"Failed to scrape generic site: {str(e)}")
    
    # Helper methods
    async def _get_text(self, page, selector: str, fallback: str = None) -> str:
        """Get text from element with fallback"""
        try:
            element = await page.query_selector(selector)
            if element:
                return (await element.text_content()).strip()
            elif fallback:
                element = await page.query_selector(fallback)
                if element:
                    return (await element.text_content()).strip()
        except:
            pass
        return ""
    
    async def _get_text_from_selectors(self, page, selectors: List[str]) -> str:
        """Try multiple selectors to get text"""
        for selector in selectors:
            text = await self._get_text(page, selector)
            if text:
                return text
        return ""
    
    async def _get_images(self, page, selectors: List[str]) -> List[str]:
        """Extract image URLs from page"""
        images = []
        
        for selector in selectors:
            try:
                elements = await page.query_selector_all(selector)
                for element in elements[:5]:  # Limit to 5 images
                    src = await element.get_attribute('src') or await element.get_attribute('data-src')
                    if src and src.startswith(('http', '//')):
                        images.append(src)
            except:
                continue
        
        return list(set(images))  # Remove duplicates
    
    async def _extract_features(self, page, selectors: List[str]) -> List[str]:
        """Extract product features from various selectors"""
        features = []
        
        for selector in selectors:
            try:
                elements = await page.query_selector_all(selector)
                for element in elements:
                    text = (await element.text_content()).strip()
                    if text and len(text) > 10 and len(text) < 200:
                        features.append(text)
            except:
                continue
        
        return features[:10]  # Limit to 10 features
    
    def _find_title(self, soup: BeautifulSoup) -> str:
        """Find product title from HTML"""
        selectors = [
            'h1[class*="title"]',
            'h1[class*="product"]',
            'h1[class*="name"]',
            '.product-title',
            '.item-title',
            'h1'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text().strip()
                if text and len(text) > 5:
                    return text
        
        # Fallback to page title
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        
        return "Unknown Product"
    
    def _find_description(self, soup: BeautifulSoup) -> str:
        """Find product description from HTML"""
        selectors = [
            '[class*="description"]',
            '[class*="overview"]',
            '[class*="detail"]',
            '.product-info',
            '.item-description'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text().strip()
                if text and len(text) > 20:
                    return text[:500]  # Limit length
        
        return ""
    
    def _find_images(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Find product images from HTML"""
        images = []
        
        # Try various image selectors
        img_elements = soup.find_all('img')
        
        for img in img_elements:
            src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
            if src:
                # Check if it's likely a product image
                if any(keyword in src.lower() for keyword in ['product', 'item', 'img', 'photo']):
                    full_url = urljoin(base_url, src)
                    if full_url not in images:
                        images.append(full_url)
        
        return images[:5]  # Limit to 5 images