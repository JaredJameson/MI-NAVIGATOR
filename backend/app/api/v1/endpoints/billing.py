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


# Mock invoices data
MOCK_INVOICES = [
    {
        "id": "INV-2026-001",
        "date": "2026-01-01",
        "amount": 99.00,
        "currency": "USD",
        "status": "paid",
        "plan": "Professional",
        "billing_period": "January 2026"
    },
    {
        "id": "INV-2025-012",
        "date": "2025-12-01",
        "amount": 99.00,
        "currency": "USD",
        "status": "paid",
        "plan": "Professional",
        "billing_period": "December 2025"
    },
    {
        "id": "INV-2025-011",
        "date": "2025-11-01",
        "amount": 99.00,
        "currency": "USD",
        "status": "paid",
        "plan": "Professional",
        "billing_period": "November 2025"
    }
]


class Invoice(BaseModel):
    id: str
    date: str
    amount: float
    currency: str
    status: str
    plan: str
    billing_period: str


@router.get("/invoices", response_model=List[Invoice])
async def list_invoices():
    """List all invoices for the current user"""
    return MOCK_INVOICES


@router.get("/invoices/{invoice_id}/download")
async def download_invoice(invoice_id: str):
    """Download invoice as PDF"""
    from fastapi.responses import Response

    # Find the invoice
    invoice = next((inv for inv in MOCK_INVOICES if inv["id"] == invoice_id), None)

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    # Generate simple PDF content (mock)
    pdf_content = f"""
%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/Resources <<
/Font <<
/F1 <<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
>>
>>
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 400
>>
stream
BT
/F1 24 Tf
100 700 Td
(INVOICE) Tj
ET
BT
/F1 12 Tf
100 650 Td
(Invoice Number: {invoice["id"]}) Tj
ET
BT
/F1 12 Tf
100 630 Td
(Date: {invoice["date"]}) Tj
ET
BT
/F1 12 Tf
100 610 Td
(Billing Period: {invoice["billing_period"]}) Tj
ET
BT
/F1 14 Tf
100 550 Td
(Plan: {invoice["plan"]}) Tj
ET
BT
/F1 14 Tf
100 520 Td
(Amount: ${invoice["amount"]:.2f} {invoice["currency"]}) Tj
ET
BT
/F1 12 Tf
100 490 Td
(Status: {invoice["status"].upper()}) Tj
ET
BT
/F1 10 Tf
100 450 Td
(Thank you for your business!) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000274 00000 n
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
724
%%EOF
""".strip()

    return Response(
        content=pdf_content.encode('latin-1'),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=invoice_{invoice_id}.pdf"
        }
    )
