from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from datetime import datetime

from app.routes.auth import get_current_user
from app.schemas.review import ReviewCreate
from app.database import review_collection, property_collection
from app.utils.notification_helper import create_notification

router = APIRouter()


def review_serializer(doc) -> dict:
    return {
        "id": str(doc["_id"]),
        "property_id": doc.get("property_id"),
        "buyer_id": doc.get("buyer_id"),
        "buyer_name": doc.get("buyer_name"),
        "rating": doc.get("rating"),
        "location": doc.get("location"),
        "property_quality": doc.get("property_quality"),
        "amenities": doc.get("amenities"),
        "value_for_money": doc.get("value_for_money"),
        "maintenance": doc.get("maintenance"),
        "overall_experience": doc.get("overall_experience"),
        "comment": doc.get("comment"),
        "status": doc.get("status", "published"),
        "created_at": doc.get("created_at").isoformat() if doc.get("created_at") else None,
    }


@router.post("/{property_id}/reviews")
async def create_review(
    property_id: str,
    payload: ReviewCreate,
    current_user: dict = Depends(get_current_user)
):
    try:
        obj_id = ObjectId(property_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid property ID format")

    prop = await property_collection.find_one({"_id": obj_id})
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    if prop.get("seller_id") == str(current_user["_id"]):
        raise HTTPException(
            status_code=400,
            detail="You cannot review your own property"
        )

    existing = await review_collection.find_one({
        "property_id": property_id,
        "buyer_id": str(current_user["_id"])
    })
    if existing:
        raise HTTPException(
            status_code=400,
            detail="You have already reviewed this property"
        )

    now = datetime.utcnow()
    doc = {
        "property_id": property_id,
        "buyer_id": str(current_user["_id"]),
        "buyer_name": current_user.get("name", "Anonymous"),
        "rating": payload.rating,
        "location": payload.location,
        "property_quality": payload.property_quality,
        "amenities": payload.amenities,
        "value_for_money": payload.value_for_money,
        "maintenance": payload.maintenance,
        "overall_experience": payload.overall_experience,
        "comment": payload.comment,
        "status": "published",
        "created_at": now,
    }

    result = await review_collection.insert_one(doc)

    try:
        await create_notification(
            user_id=prop.get("seller_id"),
            title="New review on your property ",
            body=f"{current_user.get('name', 'Buyer')} rated {payload.rating}/5",
            notif_type="system",
            reference_id=str(result.inserted_id),
            reference_type="review",
        )
    except Exception:
        pass

    return {
        "id": str(result.inserted_id),
        "status": "published"
    }


@router.get("/{property_id}/reviews")
async def list_reviews(property_id: str):
    try:
        ObjectId(property_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid property ID format")

    results = []
    total_rating = 0

    async for doc in review_collection.find({
        "property_id": property_id,
        "status": "published"
    }).sort("created_at", -1):
        results.append(review_serializer(doc))
        total_rating += doc.get("rating", 0)

    count = len(results)
    average_rating = round(total_rating / count, 1) if count > 0 else 0.0

    return {
        "average_rating": average_rating,
        "count": count,
        "results": results
    }