from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, HttpUrl
import uuid

from app.db.database import get_db
from app.models.user import User
from app.models.store import Store
from app.services.store_generator import StoreGeneratorService

router = APIRouter(prefix="/stores", tags=["stores"])

class StoreCreateRequest(BaseModel):
    product_url: HttpUrl
    store_name: str
    theme_style: str = "modern"  # modern, luxury, minimal
    brand_colors: Optional[dict] = None

class StoreResponse(BaseModel):
    id: int
    store_name: str
    source_product_url: str
    status: str
    generation_progress: int
    shopify_store_url: Optional[str] = None
    created_at: str
    
    class Config:
        from_attributes = True

class StoreGenerateResponse(BaseModel):
    store_id: int
    task_id: str
    status: str
    message: str

@router.post("/generate", response_model=StoreGenerateResponse)
async def generate_store(
    request: StoreCreateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Generate a complete Shopify store from a product URL
    """
    # Get current user for testing
    current_user = await get_current_user(db)
    
    # Check user's monthly limit
    if current_user.stores_built >= current_user.monthly_limit:
        raise HTTPException(
            status_code=403,
            detail="Monthly store generation limit reached. Please upgrade your plan."
        )
    
    # Create store record
    store = Store(
        user_id=current_user.id,
        store_name=request.store_name,
        source_product_url=str(request.product_url),
        source_platform=_detect_platform(str(request.product_url)),
        theme_style=request.theme_style,
        brand_colors=request.brand_colors or {},
        status="generating",
        generation_progress=0
    )
    
    db.add(store)
    db.commit()
    db.refresh(store)
    
    # Generate unique task ID
    task_id = str(uuid.uuid4())
    
    # Start background generation process
    background_tasks.add_task(
        _generate_store_background,
        store.id,
        task_id,
        str(request.product_url)
    )
    
    # Update user's store count
    current_user.stores_built += 1
    db.commit()
    
    return StoreGenerateResponse(
        store_id=store.id,
        task_id=task_id,
        status="generating",
        message="Store generation started. This will take 2-3 minutes."
    )

@router.get("/", response_model=List[StoreResponse])
async def list_stores(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    List all stores for the current user
    """
    current_user = await get_current_user(db)
    stores = db.query(Store).filter(
        Store.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return stores

@router.get("/{store_id}", response_model=StoreResponse)
async def get_store(
    store_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific store by ID
    """
    store = db.query(Store).filter(
        Store.id == store_id,
        Store.user_id == current_user.id
    ).first()
    
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    return store

@router.post("/{store_id}/publish")
async def publish_store(
    store_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Publish generated store to Shopify
    """
    store = db.query(Store).filter(
        Store.id == store_id,
        Store.user_id == current_user.id
    ).first()
    
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    if store.status != "completed":
        raise HTTPException(
            status_code=400,
            detail="Store must be completed before publishing"
        )
    
    # Start background publishing process
    background_tasks.add_task(_publish_store_background, store.id)
    
    return {"message": "Publishing started", "store_id": store.id}

@router.delete("/{store_id}")
async def delete_store(
    store_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a store
    """
    store = db.query(Store).filter(
        Store.id == store_id,
        Store.user_id == current_user.id
    ).first()
    
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    db.delete(store)
    db.commit()
    
    return {"message": "Store deleted successfully"}

# Helper functions
def _detect_platform(url: str) -> str:
    """Detect the source platform from URL"""
    if "aliexpress.com" in url:
        return "aliexpress"
    elif "amazon.com" in url:
        return "amazon"
    elif "ebay.com" in url:
        return "ebay"
    elif "bestbuy.com" in url:
        return "bestbuy"
    else:
        return "unknown"

async def _generate_store_background(store_id: int, task_id: str, product_url: str):
    """Background task for store generation"""
    try:
        generator = StoreGeneratorService()
        await generator.generate_complete_store(store_id, product_url)
    except Exception as e:
        # Update store with error
        # This will be implemented with proper error handling
        pass

async def _publish_store_background(store_id: int):
    """Background task for store publishing"""
    try:
        generator = StoreGeneratorService()
        await generator.publish_to_shopify(store_id)
    except Exception as e:
        # Update store with error
        # This will be implemented with proper error handling
        pass

# Temporary auth dependency - will be replaced with proper Shopify OAuth
async def get_current_user(db: Session = Depends(get_db)) -> User:
    """Temporary user for testing - replace with proper auth"""
    # This is a placeholder - real implementation will use Shopify OAuth
    return User(
        id=1,
        email="test@example.com",
        shopify_shop_domain="test-shop.myshopify.com",
        shopify_access_token="test-token",
        stores_built=0,
        monthly_limit=10
    )