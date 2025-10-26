from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON
from sqlalchemy.sql import func
from app.db.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    shopify_shop_domain = Column(String, unique=True, nullable=False)
    shopify_access_token = Column(Text, nullable=False)
    
    # Subscription info
    subscription_plan = Column(String, default="free")  # free, pro, agency
    subscription_status = Column(String, default="active")
    stores_built = Column(Integer, default=0)
    monthly_limit = Column(Integer, default=1)
    
    # Profile
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    company = Column(String, nullable=True)
    
    # Settings
    preferences = Column(JSON, default={})
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<User(email='{self.email}', shop='{self.shopify_shop_domain}')>"