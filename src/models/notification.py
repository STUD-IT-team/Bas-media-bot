# from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from models.event import Event
from notifications.NotifRegistry import NotifRegistryBase
# from enum import Enum

# class NotifType(Enum):
#     MESSAGE = "Сообщение"
#     REMINDER = "Напоминание"
#     REQUEST = "Уведомление"

# class Notification(BaseModel):
#     ID : UUID
#     Text : str
#     NotifyTime : datetime
#     # Type : NotifType
#     ChatID : int
#     EventID : UUID




class BaseNotification(metaclass=NotifRegistryBase):
    def __init__(self, id: UUID , text: str, notifyTime: datetime, chatID: int):
        self.ID = id
        self.Text = text
        self.NotifyTime = notifyTime
        self.ChatID = chatID

    def GetMessageText(self) -> str:
        """Возвращает текст сообщения (возможно сгенерированного по шаблону)"""
        raise NotImplementedError
    
    # def GetNotifyTime(self):
    #     """Возвращает время отправки сообщения"""
    #     return NotImplementedError()
    # def GetChatID(self):
    #     return NotImplementedError()
    

class EventReminderNotif(BaseNotification):
    def __init__(self, id: UUID , text: str, notifyTime: datetime, chatID: int, event: Event):
        self.Event = event
        super().__init__(id, text, notifyTime, chatID)

    def GetMessageText(self) -> str:
        msg = f"🔔 Напоминание о событии {self.Event.Name}, " + \
            f"которое пройдет {self.Event.Date} в {self.Event.Place}\n\n{self.Text}"
        return msg
    
class InfoNotif(BaseNotification):
    def __init__(self, id: UUID , text: str, notifyTime: datetime, chatID: int):
        super().__init__(id, text, notifyTime, chatID)

    def GetMessageText(self) -> str:
        return self.Text