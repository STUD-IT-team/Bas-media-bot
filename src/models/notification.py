from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from enum import Enum

class NotifType(Enum):
    MESSAGE = "Сообщение"
    REMINDER = "Напоминание"
    REQUEST = "Уведомление"

class Notification(BaseModel):
    ID : UUID
    Text : str
    NotifyTime : datetime
    Type : NotifType
    ChatID : int
    EventID : UUID