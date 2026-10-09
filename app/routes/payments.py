from fastapi import APIRouter, HTTPException, Depends, Request
from bson import ObjectId
from datetime import datetime
import uuid

from app.routes.auth import get_current_user
from app.schemas.payment import PaymentOrderCreate, PaymentVerify, PaymentWebhook
from app.database import payment_collection, booking_collection

router = APIRouter()


def payment_serializer(doc) -> dict:
    return {
        "id": str(doc["_id"]),
        "booking_id": doc.get("booking_id"),
        "buyer_id": doc.get("buyer_id"),
        "amount": doc.get("amount"),
        "currency": doc.get("currency", "INR"),
        "gateway_order_id": doc.get("gateway_order_id"),
        "gateway_payment_id": doc.get("gateway_payment_id"),
        "status": doc.get("status", "created"),
        "created_at": doc.get("created_at").isoformat() if doc.get("created_at") else None,
        "updated_at": doc.get("updated_at").isoformat() if doc.get("updated_at") else None,
    }


@router.post("/order")
async def create_payment_order(
    payload: PaymentOrderCreate,
    current_user: dict = Depends(get_current_user)
):
    try:
        booking_obj_id = ObjectId(payload.booking_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid booking ID format")

    booking = await booking_collection.find_one({"_id": booking_obj_id})
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.get("buyer_id") != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="You can only pay for your own booking")

    if payload.amount > booking.get("booking_amount", float("inf")):
        raise HTTPException(status_code=400, detail="Amount exceeds booking amount")

    gateway_order_id = f"order_{uuid.uuid4().hex[:16]}"

    now = datetime.utcnow()
    doc = {
        "booking_id": payload.booking_id,
        "buyer_id": str(current_user["_id"]),
        "amount": payload.amount,
        "currency": payload.currency,
        "gateway_order_id": gateway_order_id,
        "status": "created",
        "created_at": now,
        "updated_at": now,
    }

    result = await payment_collection.insert_one(doc)

    return {
        "payment_id": str(result.inserted_id),
        "gateway_order_id": gateway_order_id,
        "status": "created"
    }


@router.post("/verify")
async def verify_payment(
    payload: PaymentVerify,
    current_user: dict = Depends(get_current_user)
):
    try:
        obj_id = ObjectId(payload.payment_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid payment ID format")

    payment = await payment_collection.find_one({"_id": obj_id})
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if payment.get("buyer_id") != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="You can only verify your own payment")

    if not payload.signature:
        raise HTTPException(status_code=400, detail="Signature is required")

    now = datetime.utcnow()
    await payment_collection.update_one(
        {"_id": obj_id},
        {"$set": {
            "status": "paid",
            "gateway_payment_id": payload.gateway_payment_id,
            "updated_at": now
        }}
    )

    try:
        booking_obj_id = ObjectId(payment["booking_id"])
        await booking_collection.update_one(
            {"_id": booking_obj_id},
            {"$set": {"status": "confirmed", "updated_at": now}}
        )
    except Exception:
        pass

    return {
        "payment_id": payload.payment_id,
        "status": "paid"
    }


@router.post("/webhook")
async def payment_webhook(payload: PaymentWebhook, request: Request):
    try:
        obj_id = ObjectId(payload.payment_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid payment ID format")

    payment = await payment_collection.find_one({"_id": obj_id})
    if not payment:
        return {"received": True, "note": "Payment not found"}

    now = datetime.utcnow()
    await payment_collection.update_one(
        {"_id": obj_id},
        {"$set": {"status": payload.status, "updated_at": now}}
    )

    if payload.status == "paid":
        try:
            booking_obj_id = ObjectId(payment["booking_id"])
            await booking_collection.update_one(
                {"_id": booking_obj_id},
                {"$set": {"status": "confirmed", "updated_at": now}}
            )
        except Exception:
            pass

    return {"received": True}


@router.get("/{payment_id}")
async def get_payment(
    payment_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        obj_id = ObjectId(payment_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid payment ID format")

    payment = await payment_collection.find_one({"_id": obj_id})
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    user_id = str(current_user["_id"])
    role = current_user.get("role")
    is_participant = payment.get("buyer_id") == user_id or role == "admin"

    if not is_participant:
        try:
            booking = await booking_collection.find_one({"_id": ObjectId(payment["booking_id"])})
            if booking and booking.get("seller_id") == user_id:
                is_participant = True
        except Exception:
            pass

    if not is_participant:
        raise HTTPException(status_code=403, detail="Not authorized")

    return payment_serializer(payment)