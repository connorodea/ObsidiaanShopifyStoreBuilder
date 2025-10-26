import httpx
from typing import Dict, List, Optional
import asyncio
import logging

logger = logging.getLogger(__name__)

class ShopifyClient:
    """
    Shopify Admin API client for creating products, themes, and pages
    """
    
    def __init__(self, shop_domain: str, access_token: str):
        self.shop_domain = shop_domain
        self.access_token = access_token
        self.api_version = "2024-04"
        self.base_url = f"https://{shop_domain}/admin/api/{self.api_version}"
        self.timeout = 30
    
    async def create_product(self, product_data: Dict) -> Dict:
        """
        Create a new product in Shopify
        """
        url = f"{self.base_url}/products.json"
        headers = self._get_headers()
        
        payload = {
            "product": {
                "title": product_data.get("title"),
                "body_html": product_data.get("body_html", ""),
                "vendor": product_data.get("vendor", "StoreForge"),
                "product_type": product_data.get("product_type", "General"),
                "tags": product_data.get("tags", ""),
                "published": True,
                "variants": [
                    {
                        "price": product_data.get("price", "29.99"),
                        "inventory_quantity": 100,
                        "inventory_management": "shopify"
                    }
                ]
            }
        }
        
        # Add images if provided
        if product_data.get("images"):
            payload["product"]["images"] = product_data["images"]
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()["product"]
    
    async def create_page(self, page_data: Dict) -> Dict:
        """
        Create a new page in Shopify
        """
        url = f"{self.base_url}/pages.json"
        headers = self._get_headers()
        
        payload = {
            "page": {
                "title": page_data.get("title"),
                "body_html": page_data.get("body_html", ""),
                "published": page_data.get("published", True),
                "template_suffix": page_data.get("template_suffix")
            }
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()["page"]
    
    def _get_headers(self) -> Dict[str, str]:
        """
        Get standard headers for Shopify API requests
        """
        return {
            "X-Shopify-Access-Token": self.access_token,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def _generate_index_template(self, store_data: Dict) -> str:
        """
        Generate homepage template without f-string conflicts
        """
        homepage = store_data.get("homepage", {})
        hero = homepage.get("hero", {})
        
        headline = hero.get("headline", "Welcome to Our Store")
        subheadline = hero.get("subheadline", "Discover amazing products")
        cta_text = hero.get("cta_text", "Shop Now")
        
        template = '''
<div class="homepage-hero">
  <div class="hero-content">
    <h1 class="hero-headline">''' + headline + '''</h1>
    <p class="hero-subheadline">''' + subheadline + '''</p>
    <a href="/products" class="hero-cta btn">''' + cta_text + '''</a>
  </div>
</div>

<div class="featured-product">
  <div class="container">
    <h2>Featured Product</h2>
    <div class="product-showcase">
      <div class="product-image">
        {% if collections.all.products.first.featured_image %}
          <img src="{{ collections.all.products.first.featured_image | img_url: '500x500' }}" alt="{{ collections.all.products.first.title }}">
        {% endif %}
      </div>
      <div class="product-info">
        <h3>{{ collections.all.products.first.title }}</h3>
        <p>{{ collections.all.products.first.description | truncate: 200 }}</p>
        <p class="price">{{ collections.all.products.first.price | money }}</p>
        <a href="{{ collections.all.products.first.url }}" class="btn">View Product</a>
      </div>
    </div>
  </div>
</div>
        '''
        
        return template
    
    def _generate_product_template(self, store_data: Dict) -> str:
        """
        Generate product page template
        """
        return '''
<div class="product-page">
  <div class="container">
    <div class="product-gallery">
      {% for image in product.images %}
        <img src="{{ image | img_url: '600x600' }}" alt="{{ product.title }}">
      {% endfor %}
    </div>
    
    <div class="product-details">
      <h1>{{ product.title }}</h1>
      <p class="price">{{ product.price | money }}</p>
      
      <div class="product-description">
        {{ product.description }}
      </div>
      
      <form action="/cart/add" method="post" enctype="multipart/form-data">
        <select name="id">
          {% for variant in product.variants %}
            <option value="{{ variant.id }}">{{ variant.title }} - {{ variant.price | money }}</option>
          {% endfor %}
        </select>
        
        <div class="quantity-selector">
          <label for="quantity">Quantity:</label>
          <input type="number" id="quantity" name="quantity" value="1" min="1">
        </div>
        
        <button type="submit" class="btn btn-primary">Add to Cart</button>
      </form>
    </div>
  </div>
</div>
        '''