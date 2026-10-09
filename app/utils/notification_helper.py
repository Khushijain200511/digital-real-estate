from datetime import datetime
from app.database import notification_collection


async def create_notification(
    user_id: str,
    title: str,
    body: str = None,
    notif_type: str = "system",
    reference_id: str = None,
    reference_type: str = None,
    action_url: str = None,
) -> str:
   
    doc = {
        "user_id": user_id,
        "title": title,
        "body": body,
        "type": notif_type,
        "reference_id": reference_id,
        "reference_type": reference_type,
        "action_url": action_url,
        "read": False,
        "created_at": datetime.utcnow(),
    }
    result = await notification_collection.insert_one(doc)
    return str(result.inserted_id)