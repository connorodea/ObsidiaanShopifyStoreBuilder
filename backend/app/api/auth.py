from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional
import hmac
import hashlib
import base64
import urllib.parse
import httpx
import secrets
from datetime import datetime, timedelta

from app.db.database import get_db
from app.models.user import User
from app.core.config import settings
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["authentication"])

class ShopifyInstallRequest(BaseModel):
    shop: str

class ShopifyCallbackData(BaseModel):
    code: str
    hmac: str
    shop: str
    state: str
    timestamp: str

# Shopify OAuth configuration
SHOPIFY_API_KEY = settings.SHOPIFY_API_SECRET  # In production, use separate API key
SHOPIFY_API_SECRET = settings.SHOPIFY_API_SECRET
SHOPIFY_SCOPES = [
    "read_products",
    "write_products", 
    "read_themes",
    "write_themes",
    "write_script_tags",
    "read_orders",
    "write_orders"
]

@router.get("/install")
async def initiate_shopify_install(
    shop: str,
    db: Session = Depends(get_db)
):
    """
    Initiate Shopify app installation process
    """
    if not shop or not shop.endswith('.myshopify.com'):
        if not shop.endswith('.myshopify.com'):
            shop = f"{shop}.myshopify.com"
    
    # Generate random state for security
    state = secrets.token_urlsafe(32)
    
    # Store state in session/cache (in production, use Redis)
    # For now, we'll include it in the redirect and verify later
    
    # Build OAuth URL
    scopes = ",".join(SHOPIFY_SCOPES)
    redirect_uri = f"{settings.SHOPIFY_APP_URL}/api/auth/callback"
    
    oauth_url = (
        f"https://{shop}/admin/oauth/authorize?"
        f"client_id={SHOPIFY_API_KEY}&"
        f"scope={scopes}&"
        f"redirect_uri={urllib.parse.quote(redirect_uri)}&"
        f"state={state}"
    )
    
    return {
        "install_url": oauth_url,
        "shop": shop,
        "state": state
    }

@router.get("/callback")
async def shopify_callback(
    request: Request,
    code: str,
    hmac: str,
    shop: str,
    state: str,
    timestamp: str,
    db: Session = Depends(get_db)
):
    """
    Handle Shopify OAuth callback
    """
    # Verify HMAC signature
    if not _verify_webhook(request.query_params, hmac):
        raise HTTPException(status_code=400, detail="Invalid HMAC signature")
    
    # Exchange code for access token
    try:
        access_token = await _exchange_code_for_token(code, shop)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get access token: {str(e)}")
    
    # Get shop information
    try:
        shop_info = await _get_shop_info(shop, access_token)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get shop info: {str(e)}")
    
    # Create or update user
    user = db.query(User).filter(User.shopify_shop_domain == shop).first()
    
    if user:
        # Update existing user
        user.shopify_access_token = access_token
        user.email = shop_info.get("email", user.email)
        user.last_login = datetime.utcnow()
        user.is_active = True
    else:
        # Create new user
        user = User(
            email=shop_info.get("email", f"owner@{shop}"),
            shopify_shop_domain=shop,
            shopify_access_token=access_token,
            first_name=shop_info.get("shop_owner", "").split()[0] if shop_info.get("shop_owner") else None,
            last_name=" ".join(shop_info.get("shop_owner", "").split()[1:]) if shop_info.get("shop_owner") else None,
            company=shop_info.get("name", ""),
            subscription_plan="free",
            monthly_limit=1,
            is_active=True,
            is_verified=True,
            last_login=datetime.utcnow()
        )
        db.add(user)
    
    db.commit()
    db.refresh(user)
    
    # Redirect to frontend with success
    frontend_url = f"{settings.SHOPIFY_APP_URL}/dashboard?installed=true&shop={shop}"
    return RedirectResponse(url=frontend_url)

@router.post("/webhook/app/uninstalled")
async def app_uninstalled_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle app uninstall webhook from Shopify
    """
    # Verify webhook
    body = await request.body()
    hmac_header = request.headers.get("X-Shopify-Hmac-Sha256")
    
    if not _verify_webhook_body(body, hmac_header):
        raise HTTPException(status_code=400, detail="Invalid webhook signature")
    
    # Get shop domain from headers
    shop_domain = request.headers.get("X-Shopify-Shop-Domain")
    
    if shop_domain:
        # Deactivate user
        user = db.query(User).filter(User.shopify_shop_domain == shop_domain).first()
        if user:
            user.is_active = False
            user.shopify_access_token = ""  # Clear access token
            db.commit()
    
    return {"status": "success"}

@router.get("/me")
async def get_current_user_info(
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user information
    """
    # For testing, return mock user info
    test_user = await get_current_user_dependency(None, db)
    return {
        "id": test_user.id,
        "email": test_user.email,
        "shop": test_user.shopify_shop_domain,
        "subscription_plan": test_user.subscription_plan,
        "stores_built": test_user.stores_built,
        "monthly_limit": test_user.monthly_limit,
        "is_active": test_user.is_active
    }

# Helper functions
async def _exchange_code_for_token(code: str, shop: str) -> str:
    """Exchange authorization code for access token"""
    
    url = f"https://{shop}/admin/oauth/access_token"
    data = {
        "client_id": SHOPIFY_API_KEY,
        "client_secret": SHOPIFY_API_SECRET,
        "code": code
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=data)
        response.raise_for_status()
        result = response.json()
        return result["access_token"]

async def _get_shop_info(shop: str, access_token: str) -> dict:
    """Get shop information from Shopify API"""
    
    url = f"https://{shop}/admin/api/2024-04/shop.json"
    headers = {
        "X-Shopify-Access-Token": access_token,
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        result = response.json()
        return result["shop"]

def _verify_webhook(params: dict, received_hmac: str) -> bool:
    """Verify Shopify webhook HMAC signature"""
    
    # Remove hmac and signature from params
    filtered_params = {k: v for k, v in params.items() if k not in ['hmac', 'signature']}
    
    # Sort and encode parameters
    sorted_params = sorted(filtered_params.items())
    query_string = urllib.parse.urlencode(sorted_params)
    
    # Calculate HMAC
    calculated_hmac = hmac.new(
        SHOPIFY_API_SECRET.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(calculated_hmac, received_hmac)

def _verify_webhook_body(body: bytes, received_hmac: str) -> bool:
    """Verify Shopify webhook body HMAC signature"""
    
    if not received_hmac:
        return False
    
    calculated_hmac = base64.b64encode(
        hmac.new(
            SHOPIFY_API_SECRET.encode('utf-8'),
            body,
            hashlib.sha256
        ).digest()
    ).decode('utf-8')
    
    return hmac.compare_digest(calculated_hmac, received_hmac)

# Dependency for getting current user (simplified version)
async def get_current_user_dependency(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from session/token
    In production, this would validate JWT tokens or session cookies
    """
    
    # For development, we'll use shop parameter or create a test user
    shop = request.query_params.get("shop")
    
    if shop:
        user = db.query(User).filter(User.shopify_shop_domain == shop).first()
        if user and user.is_active:
            return user
    
    # For testing purposes, return or create a test user
    test_user = db.query(User).filter(User.email == "test@storeforge.ai").first()
    if not test_user:
        test_user = User(
            email="test@storeforge.ai",
            shopify_shop_domain="test-shop.myshopify.com",
            shopify_access_token="test-token",
            subscription_plan="pro",
            monthly_limit=10,
            stores_built=0,
            is_active=True,
            is_verified=True
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
    
    return test_user