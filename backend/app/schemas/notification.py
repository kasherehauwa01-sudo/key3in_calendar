from datetime import date, datetime

from pydantic import BaseModel


class NotificationRead(BaseModel):
    note_id: int
    date: date
    user_id: int
    user_name: str
    user_color: str
    text: str
    created_at: datetime
    is_read: bool
