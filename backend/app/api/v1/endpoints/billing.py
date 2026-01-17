"""
Billing and Payment Methods API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

# In-memory storage for payment methods (for development)
PAYMENT_METHODS = {}

class PaymentMethod(BaseModel):
    id: str
    card_last4: str
    card_brand: str  # visa, mastercard, amex
    card_exp_month: int
    card_exp_year: int
    is_default: bool
    created_at: str

class AddPaymentMethodRequest(BaseModel):
    card_number: str
    card_exp_month: int
    card_exp_year: int
    card_cvc: str
    cardholder_name: str

class SetDefaultRequest(BaseModel):
    payment_method_id: str


@router.get("/payment-methods", response_model=List[PaymentMethod])
async def list_payment_methods():
    """List all payment methods for the current user"""
    # In production, this would filter by user_id
    user_id = "user_001"  # Mock user ID

    if user_id not in PAYMENT_METHODS:
        PAYMENT_METHODS[user_id] = []

    return PAYMENT_METHODS[user_id]


@router.post("/payment-methods", response_model=PaymentMethod)
async def add_payment_method(request: AddPaymentMethodRequest):
    """Add a new payment method"""
    user_id = "user_001"  # Mock user ID

    if user_id not in PAYMENT_METHODS:
        PAYMENT_METHODS[user_id] = []

    # Extract last 4 digits
    card_last4 = request.card_number[-4:]

    # Determine card brand from first digit (simplified)
    first_digit = request.card_number[0]
    if first_digit == '4':
        card_brand = 'visa'
    elif first_digit == '5':
        card_brand = 'mastercard'
    elif first_digit == '3':
        card_brand = 'amex'
    else:
        card_brand = 'visa'  # default

    # Generate ID
    payment_method_id = f"pm_{len(PAYMENT_METHODS[user_id]) + 1:03d}"

    # Check if this is the first payment method (make it default)
    is_default = len(PAYMENT_METHODS[user_id]) == 0

    # Create payment method
    payment_method = PaymentMethod(
        id=payment_method_id,
        card_last4=card_last4,
        card_brand=card_brand,
        card_exp_month=request.card_exp_month,
        card_exp_year=request.card_exp_year,
        is_default=is_default,
        created_at=datetime.now().isoformat()
    )

    PAYMENT_METHODS[user_id].append(payment_method)

    return payment_method


@router.post("/payment-methods/set-default")
async def set_default_payment_method(request: SetDefaultRequest):
    """Set a payment method as default"""
    user_id = "user_001"  # Mock user ID

    if user_id not in PAYMENT_METHODS or not PAYMENT_METHODS[user_id]:
        raise HTTPException(status_code=404, detail="No payment methods found")

    # Find the payment method
    found = False
    for pm in PAYMENT_METHODS[user_id]:
        if pm.id == request.payment_method_id:
            pm.is_default = True
            found = True
        else:
            pm.is_default = False

    if not found:
        raise HTTPException(status_code=404, detail="Payment method not found")

    return {"message": "Default payment method updated", "payment_method_id": request.payment_method_id}


@router.delete("/payment-methods/{payment_method_id}")
async def remove_payment_method(payment_method_id: str):
    """Remove a payment method"""
    user_id = "user_001"  # Mock user ID

    if user_id not in PAYMENT_METHODS or not PAYMENT_METHODS[user_id]:
        raise HTTPException(status_code=404, detail="No payment methods found")

    # Find and remove the payment method
    original_length = len(PAYMENT_METHODS[user_id])
    PAYMENT_METHODS[user_id] = [pm for pm in PAYMENT_METHODS[user_id] if pm.id != payment_method_id]

    if len(PAYMENT_METHODS[user_id]) == original_length:
        raise HTTPException(status_code=404, detail="Payment method not found")

    # If we removed the default payment method, set another as default
    if PAYMENT_METHODS[user_id] and not any(pm.is_default for pm in PAYMENT_METHODS[user_id]):
        PAYMENT_METHODS[user_id][0].is_default = True

    return {"message": "Payment method removed", "payment_method_id": payment_method_id}
