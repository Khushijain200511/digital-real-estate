from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId

from app.routes.auth import get_current_user
from app.routes.properties import property_serializer
from app.schemas.user import UserProfileResponse, UserUpdateRequest
from app.database import user_collection, property_collection

router = APIRouter()


@router.get("/me", response_model=UserProfileResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "id": str(current_user["_id"]),
        "name": current_user.get("name", ""),
        "email": current_user.get("email", ""),
        "mobile": current_user.get("mobile"),
        "role": current_user.get("role", "buyer"),
        "is_verified": current_user.get("is_verified", False),
    }


@router.patch("/me")
async def update_me(
    update_data: UserUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    update_fields = {}

    if update_data.name is not None:
        update_fields["name"] = update_data.name

    if update_data.mobile is not None:
        existing = await user_collection.find_one({
            "mobile": update_data.mobile,
            "_id": {"$ne": current_user["_id"]}
        })
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Mobile number already in use by another account"
            )
        update_fields["mobile"] = update_data.mobile

    if not update_fields:
        return {
            "message": "No fields to update",
            "updated_fields": []
        }

    await user_collection.update_one(
        {"_id": current_user["_id"]},
        {"$set": update_fields}
    )

    return {
        "message": "Profile updated",
        "updated_fields": list(update_fields.keys())
    }


@router.post("/me/saved-properties/{property_id}")
async def save_property(
    property_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        obj_id = ObjectId(property_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid property ID format")

    prop = await property_collection.find_one({"_id": obj_id})
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    saved = current_user.get("saved_properties", [])
    if property_id in saved:
        return {
            "message": "Property already saved",
            "property_id": property_id
        }

    await user_collection.update_one(
        {"_id": current_user["_id"]},
        {"$addToSet": {"saved_properties": property_id}}
    )

    return {
        "message": "Property saved",
        "property_id": property_id
    }


@router.delete("/me/saved-properties/{property_id}")
async def unsave_property(
    property_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        ObjectId(property_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid property ID format")

    result = await user_collection.update_one(
        {"_id": current_user["_id"]},
        {"$pull": {"saved_properties": property_id}}
    )

    if result.modified_count == 0:
        return {
            "message": "Property was not in saved list",
            "property_id": property_id
        }

    return {
        "message": "Property removed from saved properties",
        "property_id": property_id
    }


@router.get("/me/saved-properties")
async def list_saved_properties(
    current_user: dict = Depends(get_current_user)
):
    saved_ids = current_user.get("saved_properties", [])

    if not saved_ids:
        return {
            "count": 0,
            "results": []
        }

    object_ids = []
    for pid in saved_ids:
        try:
            object_ids.append(ObjectId(pid))
        except Exception:
            continue

    results = []
    async for prop in property_collection.find({"_id": {"$in": object_ids}}):
        results.append(property_serializer(prop))

    return {
        "count": len(results),
        "results": results
    }