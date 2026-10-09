from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from datetime import datetime

from app.routes.auth import get_current_user
from app.schemas.saved_search import SavedSearchCreate, SavedSearchUpdate
from app.database import saved_search_collection

router = APIRouter()


def saved_search_serializer(doc) -> dict:
    return {
        "id": str(doc["_id"]),
        "name": doc.get("name"),
        "city": doc.get("city"),
        "locality": doc.get("locality"),
        "property_type": doc.get("property_type"),
        "min_budget": doc.get("min_budget"),
        "max_budget": doc.get("max_budget"),
        "bhk": doc.get("bhk"),
        "parking": doc.get("parking"),
        "possession_status": doc.get("possession_status"),
        "amenities": doc.get("amenities", []),
        "created_at": doc.get("created_at").isoformat() if doc.get("created_at") else None,
        "updated_at": doc.get("updated_at").isoformat() if doc.get("updated_at") else None,
    }


@router.post("/")
async def create_saved_search(
    search_data: SavedSearchCreate,
    current_user: dict = Depends(get_current_user)
):
    doc = search_data.dict()
    doc["user_id"] = str(current_user["_id"])
    doc["created_at"] = datetime.utcnow()
    doc["updated_at"] = datetime.utcnow()

    result = await saved_search_collection.insert_one(doc)

    return {
        "id": str(result.inserted_id),
        "message": "Saved search created"
    }


@router.get("/")
async def list_saved_searches(
    current_user: dict = Depends(get_current_user)
):
    results = []
    cursor = saved_search_collection.find(
        {"user_id": str(current_user["_id"])}
    ).sort("created_at", -1)

    async for doc in cursor:
        results.append(saved_search_serializer(doc))

    return {
        "count": len(results),
        "results": results
    }


@router.patch("/{search_id}")
async def update_saved_search(
    search_id: str,
    update_data: SavedSearchUpdate,
    current_user: dict = Depends(get_current_user)
):
    try:
        obj_id = ObjectId(search_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid search ID format")

    existing = await saved_search_collection.find_one({"_id": obj_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Saved search not found")

    if existing["user_id"] != str(current_user["_id"]):
        raise HTTPException(
            status_code=403,
            detail="You can only update your own saved searches"
        )

    update_fields = {k: v for k, v in update_data.dict().items() if v is not None}

    if not update_fields:
        return {
            "message": "No fields to update",
            "updated_fields": []
        }

    update_fields["updated_at"] = datetime.utcnow()

    await saved_search_collection.update_one(
        {"_id": obj_id},
        {"$set": update_fields}
    )

    return {
        "message": "Saved search updated",
        "updated_fields": list(update_fields.keys())
    }


@router.delete("/{search_id}")
async def delete_saved_search(
    search_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        obj_id = ObjectId(search_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid search ID format")

    existing = await saved_search_collection.find_one({"_id": obj_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Saved search not found")

    if existing["user_id"] != str(current_user["_id"]):
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own saved searches"
        )

    await saved_search_collection.delete_one({"_id": obj_id})

    return {
        "message": "Saved search deleted"
    }