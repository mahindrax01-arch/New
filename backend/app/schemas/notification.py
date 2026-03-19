from datetime import datetime

from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: str
    user_id: str
    type: str
    message: str
    data: dict
    is_read: bool
    created_at: datetime
