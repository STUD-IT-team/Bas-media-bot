# from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from models.event import Event
from notifications.NotifRegistry import NotifRegistryBase

"""Маппер для БД"""
class MapperNotification:
    __mapClsNmType = {
        'EventReminderNotif': 'EventReminder',
        'InfoNotif': 'Info',
        'AssignmentNotif': 'Assignment',
        'EventRemoveNotif': 'EventRemove'
        
    }
    __mapTypeClsNm = {v: k for k, v in __mapClsNmType.items()}

    @classmethod
    def GetClassNameByType(cls, type: str) -> str:
        return cls.__mapTypeClsNm[type]
    
    @classmethod
    def GetTypeByClassName(cls, clsName: str) -> str:
        return cls.__mapClsNmType[clsName]


class BaseNotification(metaclass=NotifRegistryBase):
    def __init__(self, id: UUID , text: str, notifyTime: datetime, ChatIDs: list[int]):
        self.ID = id
        self.Text = text
        self.NotifyTime = notifyTime
        self.ChatIDs = ChatIDs

    def GetMessageText(self) -> str:
        """Возвращает текст сообщения (возможно сгенерированного по шаблону)"""
        raise NotImplementedError
    
    @classmethod
    def RelatedToEvent(self) -> bool:
        raise NotImplementedError
    
    def GetEventID(self) -> UUID:
        raise NotImplementedError
    
    def __str__(self):
        raise NotImplementedError
    

class BaseNotifWithEvent(BaseNotification):
    @classmethod
    def RelatedToEvent(self) -> bool:
        return True
    
    def GetEventID(self) -> UUID:
        return self.Event.ID


class EventReminderNotif(BaseNotifWithEvent):
    def __init__(self, id: UUID , text: str, notifyTime: datetime, ChatIDs: list[int], event: Event):
        self.Event = event
        super().__init__(id, text, notifyTime, ChatIDs)

    def GetMessageText(self) -> str:
        msg = f"🔔 Напоминание о событии \"{self.Event.Name}\", " + \
            f"которое пройдет {self.Event.Date} в {self.Event.Place}\n\n{self.Text}"
        return msg
    
    def __str__(self):
        return f"EventReminderNotif(id={str(self.ID)[:4]}, text={self.Text[:7]}, chats={self.ChatIDs}, time={self.NotifyTime}, event={self.Event.Name})"
    
class AssignmentNotif(BaseNotifWithEvent):
    def __init__(self, id: UUID , text: str, notifyTime: datetime, ChatIDs: list[int], event: Event):
        self.Event = event
        super().__init__(id, text, notifyTime, ChatIDs)

    def GetMessageText(self) -> str:
        msg = f"Уведомление о назначении на событие \"{self.Event.Name}\", " + \
            f"которое пройдет {self.Event.Date} в {self.Event.Place}\n\n{self.Text}"
        return msg

    def __str__(self):
        return f"AssignmentNotif(id={str(self.ID)[:4]}, text={self.Text[:7]}, chats={self.ChatIDs}, time={self.NotifyTime}, event={self.Event.Name})"

class EventRemoveNotif(BaseNotifWithEvent):
    def __init__(self, id: UUID , text: str, notifyTime: datetime, ChatIDs: list[int], event: Event):
        self.Event = event
        super().__init__(id, text, notifyTime, ChatIDs)

    def GetMessageText(self) -> str:
        msg = f"Уведомление об отмене мепрориятия \"{self.Event.Name}\" \n\n{self.Text}, "
        return msg
    
    def __str__(self):
        return f"EventRemoveNotif(id={str(self.ID)[:4]}, text={self.Text[:7]}, chats={self.ChatIDs}, time={self.NotifyTime}, event={self.Event.Name})"


class InfoNotif(BaseNotification):
    def __init__(self, id: UUID , text: str, notifyTime: datetime, ChatIDs: list[int]):
        super().__init__(id, text, notifyTime, ChatIDs)

    def GetMessageText(self) -> str:
        return self.Text
    
    @classmethod
    def RelatedToEvent(self) -> bool:
        return False
    
    def GetEventID(self) -> UUID:
        return None
    
    def __str__(self):
        return f"InfoNotif(id={str(self.ID)[:4]}, text={self.Text[:15]}, chats={self.ChatIDs}, time={self.NotifyTime})"
    

