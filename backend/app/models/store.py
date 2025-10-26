from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class Store(Base):
    __tablename__ = "stores"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Store identification
    store_name = Column(String, nullable=False)
    shopify_theme_id = Column(String, nullable=True)
    shopify_store_url = Column(String, nullable=True)
    
    # Source product info
    source_product_url = Column(Text, nullable=False)
    source_platform = Column(String, nullable=False)  # aliexpress, amazon, etc.
    
    # Generated content
    ai_generated_content = Column(JSON, default={})
    enhanced_images = Column(JSON, default=[])
    
    # Store configuration
    theme_style = Column(String, default="modern")  # modern, luxury, minimal
    brand_colors = Column(JSON, default={})
    store_pages = Column(JSON, default={})
    
    # Status
    status = Column(String, default="draft")  # draft, generating, published, error
    generation_progress = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    
    # SEO and analytics
    seo_title = Column(String, nullable=True)
    seo_description = Column(Text, nullable=True)
    seo_keywords = Column(JSON, default=[])
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationship
    user = relationship("User", back_populates="stores")
    
    def __repr__(self):
        return f"<Store(name='{self.store_name}', status='{self.status}')>"


# Add relationship to User model
from app.models.user import User
User.stores = relationship("Store", back_populates="user")