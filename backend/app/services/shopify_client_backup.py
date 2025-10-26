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
    
    async def get_themes(self) -> List[Dict]:
        """
        Get all themes for the shop
        """
        url = f"{self.base_url}/themes.json"
        headers = self._get_headers()
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()["themes"]
    
    async def get_main_theme(self) -> Optional[Dict]:
        """
        Get the main/published theme
        """
        themes = await self.get_themes()
        for theme in themes:
            if theme.get("role") == "main":
                return theme
        return None
    
    async def update_theme_asset(self, theme_id: str, asset_key: str, asset_value: str) -> Dict:
        """
        Update a theme asset (template, CSS, etc.)
        """
        url = f"{self.base_url}/themes/{theme_id}/assets.json"
        headers = self._get_headers()
        
        payload = {
            "asset": {
                "key": asset_key,
                "value": asset_value
            }
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.put(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()["asset"]
    
    async def create_custom_theme_files(self, theme_id: str, store_data: Dict) -> List[Dict]:
        """
        Create custom theme files for the generated store
        """
        results = []
        
        # Update index.liquid template
        index_template = self._generate_index_template(store_data)
        result = await self.update_theme_asset(
            theme_id, 
            "templates/index.liquid", 
            index_template
        )
        results.append(result)
        
        # Update product template
        product_template = self._generate_product_template(store_data)
        result = await self.update_theme_asset(
            theme_id,
            "templates/product.liquid",
            product_template
        )
        results.append(result)
        
        # Add custom CSS
        custom_css = self._generate_custom_css(store_data)
        result = await self.update_theme_asset(
            theme_id,
            "assets/custom.css",
            custom_css
        )
        results.append(result)
        
        return results
    
    async def create_collection(self, collection_data: Dict) -> Dict:
        """
        Create a product collection
        """
        url = f"{self.base_url}/custom_collections.json"
        headers = self._get_headers()
        
        payload = {
            "custom_collection": {
                "title": collection_data.get("title"),
                "body_html": collection_data.get("body_html", ""),
                "published": True
            }
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()["custom_collection"]
    
    async def add_product_to_collection(self, collection_id: str, product_id: str) -> Dict:
        """
        Add a product to a collection
        """
        url = f"{self.base_url}/collects.json"
        headers = self._get_headers()
        
        payload = {
            "collect": {
                "product_id": product_id,
                "collection_id": collection_id
            }
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()["collect"]
    
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
        Generate homepage template
        """
        homepage = store_data.get("homepage", {})
        hero = homepage.get("hero", {})
        featured_product = homepage.get("featured_product", {})
        
        # Build template without f-strings to avoid Liquid conflicts
        headline = hero.get("headline", "Welcome to Our Store")
        subheadline = hero.get("subheadline", "Discover amazing products")
        cta_text = hero.get("cta_text", "Shop Now")
        features_headline = homepage.get("features_section", {}).get("headline", "Why Choose Us")
        
        template = """
<div class="homepage-hero">
  <div class="hero-content">
    <h1 class="hero-headline">{hero.get("headline", "Welcome to Our Store")}</h1>
    <p class="hero-subheadline">{hero.get("subheadline", "Discover amazing products")}</p>
    <a href="/products" class="hero-cta btn">{hero.get("cta_text", "Shop Now")}</a>
  </div>
</div>

<div class="featured-product">
  <div class="container">
    <h2>Featured Product</h2>
    <div class="product-showcase">
      <div class="product-image">
        {% if collections.all.products.first.featured_image %}
          <img src="{{{{ collections.all.products.first.featured_image | img_url: '500x500' }}}}" alt="{{{{ collections.all.products.first.title }}}}">
        {% endif %}
      </div>
      <div class="product-info">
        <h3>{{{{ collections.all.products.first.title }}}}</h3>
        <p>{{{{ collections.all.products.first.description | truncate: 200 }}}}</p>
        <p class="price">{{{{ collections.all.products.first.price | money }}}}</p>
        <a href="{{{{ collections.all.products.first.url }}}}" class="btn">View Product</a>
      </div>
    </div>
  </div>
</div>

<div class="features-section">
  <div class="container">
    <h2>{homepage.get("features_section", {}).get("headline", "Why Choose Us")}</h2>
    <div class="features-grid">
      {% assign features = "{', '.join(homepage.get('features_section', {}).get('features', []))}" | split: ', ' %}
      {% for feature in features %}
        <div class="feature-item">
          <h3>{{{{ feature }}}}</h3>
        </div>
      {% endfor %}
    </div>
  </div>
</div>
        """
    
    def _generate_product_template(self, store_data: Dict) -> str:
        """
        Generate product page template
        """
        product_data = store_data.get("product", {})
        
        return """
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
        """
    
    def _generate_custom_css(self, store_data: Dict) -> str:
        """
        Generate custom CSS based on theme configuration
        """
        theme = store_data.get("theme", {})
        colors = theme.get("colors", {})
        fonts = theme.get("fonts", {})
        
        return f"""
/* StoreForge Custom Styles */
:root {{
  --primary-color: {colors.get("primary", "#3b82f6")};
  --secondary-color: {colors.get("secondary", "#64748b")};
  --accent-color: {colors.get("accent", "#f59e0b")};
  --background-color: {colors.get("background", "#ffffff")};
  --text-color: {colors.get("text", "#1f2937")};
  --primary-font: {fonts.get("primary", "Inter, sans-serif")};
  --secondary-font: {fonts.get("secondary", "System UI, sans-serif")};
}}

body {{
  font-family: var(--primary-font);
  color: var(--text-color);
  background-color: var(--background-color);
}}

.homepage-hero {{
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  color: white;
  padding: 100px 0;
  text-align: center;
}}

.hero-headline {{
  font-size: 3rem;
  font-weight: bold;
  margin-bottom: 1rem;
}}

.hero-subheadline {{
  font-size: 1.25rem;
  margin-bottom: 2rem;
  opacity: 0.9;
}}

.btn {{
  display: inline-block;
  padding: 12px 24px;
  background-color: var(--accent-color);
  color: white;
  text-decoration: none;
  border-radius: 6px;
  font-weight: 600;
  transition: background-color 0.3s;
}}

.btn:hover {{
  background-color: var(--primary-color);
}}

.featured-product {{
  padding: 80px 0;
}}

.product-showcase {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
  align-items: center;
}}

.features-section {{
  background-color: #f8f9fa;
  padding: 80px 0;
}}

.features-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
  margin-top: 40px;
}}

.feature-item {{
  text-align: center;
  padding: 30px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}}

.container {{
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}}

@media (max-width: 768px) {{
  .product-showcase {{
    grid-template-columns: 1fr;
  }}
  
  .hero-headline {{
    font-size: 2rem;
  }}
}}
        """