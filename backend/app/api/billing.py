from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
import stripe
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.db.database import get_db
from app.models.user import User
from app.core.config import settings
from app.api.auth import get_current_user_dependency

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

router = APIRouter(prefix="/billing", tags=["billing"])

class SubscriptionPlan(BaseModel):
    id: str
    name: str
    price: int  # in cents
    interval: str  # 'month' or 'year'
    features: List[str]
    store_limit: int

class CreateCheckoutRequest(BaseModel):
    plan_id: str
    success_url: str
    cancel_url: str

class SubscriptionResponse(BaseModel):
    id: str
    status: str
    current_period_start: str
    current_period_end: str
    plan_name: str
    price: int
    store_limit: int
    stores_used: int

# Define subscription plans
SUBSCRIPTION_PLANS = {
    "free": SubscriptionPlan(
        id="free",
        name="Free",
        price=0,
        interval="month",
        features=[
            "1 store generation",
            "AI content generation",
            "Basic image enhancement",
            "Standard themes"
        ],
        store_limit=1
    ),
    "pro": SubscriptionPlan(
        id="price_pro_monthly",  # Stripe price ID
        name="Pro",
        price=3900,  # $39.00
        interval="month",
        features=[
            "10 stores per month",
            "Advanced AI models",
            "Premium image enhancement",
            "Premium themes",
            "CSV bulk import",
            "Priority support",
            "SEO optimization"
        ],
        store_limit=10
    ),
    "agency": SubscriptionPlan(
        id="price_agency_monthly",  # Stripe price ID
        name="Agency",
        price=9900,  # $99.00
        interval="month",
        features=[
            "Unlimited stores",
            "White-label options",
            "Custom branding",
            "API access",
            "Dedicated support",
            "Team collaboration",
            "Advanced analytics"
        ],
        store_limit=999999
    )
}

@router.get("/plans")
async def get_subscription_plans():
    """
    Get all available subscription plans
    """
    return {
        "plans": list(SUBSCRIPTION_PLANS.values())
    }

@router.get("/subscription")
async def get_current_subscription(
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Get current user's subscription information
    """
    if current_user.subscription_plan == "free":
        return SubscriptionResponse(
            id="free",
            status="active",
            current_period_start=datetime.utcnow().isoformat(),
            current_period_end=(datetime.utcnow() + timedelta(days=30)).isoformat(),
            plan_name="Free",
            price=0,
            store_limit=current_user.monthly_limit,
            stores_used=current_user.stores_built
        )
    
    # For paid plans, get subscription from Stripe
    try:
        # In a real implementation, you'd store the Stripe customer ID
        # For now, we'll return mock data
        plan = SUBSCRIPTION_PLANS.get(current_user.subscription_plan)
        if not plan:
            raise HTTPException(status_code=404, detail="Subscription plan not found")
        
        return SubscriptionResponse(
            id=f"sub_{current_user.id}",
            status=current_user.subscription_status,
            current_period_start=datetime.utcnow().isoformat(),
            current_period_end=(datetime.utcnow() + timedelta(days=30)).isoformat(),
            plan_name=plan.name,
            price=plan.price,
            store_limit=current_user.monthly_limit,
            stores_used=current_user.stores_built
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get subscription: {str(e)}")

@router.post("/create-checkout-session")
async def create_checkout_session(
    request: CreateCheckoutRequest,
    current_user: User = Depends(get_current_user_dependency)
):
    """
    Create a Stripe checkout session for subscription upgrade
    """
    try:
        plan = None
        for p in SUBSCRIPTION_PLANS.values():
            if p.id == request.plan_id:
                plan = p
                break
        
        if not plan or plan.id == "free":
            raise HTTPException(status_code=400, detail="Invalid plan selected")
        
        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': plan.id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.success_url + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.cancel_url,
            customer_email=current_user.email,
            metadata={
                'user_id': str(current_user.id),
                'plan_id': plan.id,
                'shop_domain': current_user.shopify_shop_domain
            }
        )
        
        return {
            'checkout_url': checkout_session.url,
            'session_id': checkout_session.id
        }
        
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create checkout session: {str(e)}")

@router.post("/portal")
async def create_customer_portal(
    current_user: User = Depends(get_current_user_dependency)
):
    """
    Create a Stripe customer portal session for managing subscription
    """
    try:
        # In production, you'd retrieve the customer ID from your database
        # For now, we'll create a mock portal URL
        
        if current_user.subscription_plan == "free":
            raise HTTPException(status_code=400, detail="No active subscription to manage")
        
        # Mock portal session (in production, use actual Stripe customer portal)
        portal_url = f"{settings.SHOPIFY_APP_URL}/billing/manage"
        
        return {
            'portal_url': portal_url
        }
        
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create portal session: {str(e)}")

@router.post("/webhook")
async def handle_stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle Stripe webhooks for subscription events
    """
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle different event types
    if event['type'] == 'checkout.session.completed':
        await _handle_checkout_completed(event['data']['object'], db)
    elif event['type'] == 'customer.subscription.updated':
        await _handle_subscription_updated(event['data']['object'], db)
    elif event['type'] == 'customer.subscription.deleted':
        await _handle_subscription_cancelled(event['data']['object'], db)
    elif event['type'] == 'invoice.payment_succeeded':
        await _handle_payment_succeeded(event['data']['object'], db)
    elif event['type'] == 'invoice.payment_failed':
        await _handle_payment_failed(event['data']['object'], db)
    
    return {'status': 'success'}

@router.get("/usage")
async def get_usage_stats(
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Get current usage statistics for the user
    """
    # Calculate usage for current billing period
    current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # In production, you'd query actual usage from the database
    # For now, return current user data
    
    return {
        "current_plan": current_user.subscription_plan,
        "stores_limit": current_user.monthly_limit,
        "stores_used": current_user.stores_built,
        "stores_remaining": max(0, current_user.monthly_limit - current_user.stores_built),
        "usage_percentage": min(100, (current_user.stores_built / current_user.monthly_limit) * 100),
        "billing_period_start": current_month_start.isoformat(),
        "billing_period_end": (current_month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1),
        "can_create_store": current_user.stores_built < current_user.monthly_limit
    }

# Helper functions for webhook handling
async def _handle_checkout_completed(session, db: Session):
    """Handle successful checkout completion"""
    user_id = session.get('metadata', {}).get('user_id')
    plan_id = session.get('metadata', {}).get('plan_id')
    
    if user_id and plan_id:
        user = db.query(User).filter(User.id == int(user_id)).first()
        if user:
            # Update user's subscription
            if plan_id == "price_pro_monthly":
                user.subscription_plan = "pro"
                user.monthly_limit = 10
            elif plan_id == "price_agency_monthly":
                user.subscription_plan = "agency"
                user.monthly_limit = 999999
            
            user.subscription_status = "active"
            user.stores_built = 0  # Reset monthly counter
            db.commit()

async def _handle_subscription_updated(subscription, db: Session):
    """Handle subscription updates"""
    # Update user subscription status based on Stripe data
    pass

async def _handle_subscription_cancelled(subscription, db: Session):
    """Handle subscription cancellation"""
    # Downgrade user to free plan
    pass

async def _handle_payment_succeeded(invoice, db: Session):
    """Handle successful payment"""
    # Reset monthly usage counters
    pass

async def _handle_payment_failed(invoice, db: Session):
    """Handle failed payment"""
    # Mark subscription as past due
    pass