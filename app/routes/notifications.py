from fastapi import APIRouter, HTTPException, Depends, Query
from bson import ObjectId

from app.routes.auth import get_current_user
from app.database import notification_collection

router = APIRouter()


def notification_serializer(doc) -> dict:
    return {
        "id": str(doc["_id"]),
        "title": doc.get("title"),
        "body": doc.get("body"),
        "type": doc.get("type", "system"),
        "reference_id": doc.get("reference_id"),
        "reference_type": doc.get("reference_type"),
        "action_url": doc.get("action_url"),
        "read": doc.get("read", False),
        "created_at": doc.get("created_at").isoformat() if doc.get("created_at") else None,
    }



@router.get("/")
async def list_notifications(
    unread_only: bool = Query(False, description="Only show unread"),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
):
  
    
    query = {"user_id": str(current_user["_id"])}
    if unread_only:
        query["read"] = False
    
    results = []
    unread_count = 0
    async for doc in notification_collection.find(query).sort("created_at", -1).limit(limit):
        results.append(notification_serializer(doc))
        if not doc.get("read", False):
            unread_count += 1
    
    return {
        "count": len(results),
        "unread_count": unread_count,
        "results": results,
    }



@router.patch("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user),
):
  
    
    try:
        obj_id = ObjectId(notification_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid notification ID format")
    
    notif = await notification_collection.find_one({"_id": obj_id})
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    
   
    if notif.get("user_id") != str(current_user["_id"]):
        raise HTTPException(
            status_code=403,
            detail="You can only update your own notifications"
        )
    
    await notification_collection.update_one(
        {"_id": obj_id},
        {"$set": {"read": True}}
    )
    
    return {
        "id": notification_id,
        "read": True,
    }



@router.patch("/read-all")
async def mark_all_read(
    current_user: dict = Depends(get_current_user),
):
    """Mark all notifications of the current user as read."""
    
    result = await notification_collection.update_many(
        {"user_id": str(current_user["_id"]), "read": False},
        {"$set": {"read": True}}
    )
    
    return {
        "message": f"{result.modified_count} notifications marked as read",
        "modified_count": result.modified_count,
    }