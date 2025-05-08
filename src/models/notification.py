from uuid import UUID
from datetime import datetime
from enum import StrEnum
from models.event import Event


class TypeNotif(StrEnum):
    EVENT_REMINDER = "event_reminder"
    INFO = "info"
    ASSIGNMENT = "assignment"
    EVENT_REMOVE = "event_remove"

class BaseNotification:
    pass

class NotifRegistryBase(type):
    __NOTIF_REGISTRY = {} # map[TypeNotif] -> class

    def __new__(cls, name, bases, atrs):
        new_cls = type.__new__(cls, name, bases, atrs)
        if new_cls.TYPE is not None:
            cls.__NOTIF_REGISTRY[new_cls.TYPE] = new_cls
        return new_cls
    
    def Create(type: TypeNotif, id: UUID , text: str, notifyTime: datetime, ChatIDs: list[int], event: Event):
        if type not in list(TypeNotif):
            all_types = list(TypeNotif.__members__.keys())
            raise Exception(f"Попытка создать класс несуществующего типа. Все типы TypeNotif: {', '.join(all_types)}")
        return NotifRegistryBase.__NOTIF_REGISTRY[type](
            id=id,
            text=text,
            notifyTime=notifyTime,
            ChatIDs=ChatIDs,
            event=event
        )


class BaseNotification(metaclass=NotifRegistryBase):
    TYPE = None

    def __init__(self, id: UUID , text: str, notifyTime: datetime, ChatIDs: list[int], **kwargs):
        self.ID = id
        self.Text = text
        self.NotifyTime = notifyTime
        self.ChatIDs = ChatIDs

    def GetMessageText(self) -> str:
        """Возвращает текст сообщения (возможно сгенерированного по шаблону)"""
        raise NotImplementedError
    
    def GetEventID(self) -> UUID:
        raise NotImplementedError
    
    def __str__(self):
        raise NotImplementedError
    

class BaseNotifWithEvent(BaseNotification):
    TYPE = None
    def GetEventID(self) -> UUID:
        return self.Event.ID


class EventReminderNotif(BaseNotifWithEvent):
    TYPE = TypeNotif.EVENT_REMINDER

    def __init__(self, id: UUID , text: str, notifyTime: datetime, ChatIDs: list[int], event: Event, **kwargs):
        self.Event = event
        super().__init__(id, text, notifyTime, ChatIDs, **kwargs)

    def GetMessageText(self) -> str:
        msg = f"🔔 Напоминание о событии \"{self.Event.Name}\", " + \
            f"которое пройдет {self.Event.Date} в {self.Event.Place}\n{self.Text}"
        return msg
    
    def __str__(self):
        return f"EventReminderNotif(id={str(self.ID)[:4]}, text={self.Text[:7]}, chats={self.ChatIDs}, time={self.NotifyTime}, event={self.Event.Name})"
    
class AssignmentNotif(BaseNotifWithEvent):
    TYPE = TypeNotif.ASSIGNMENT

    def __init__(self, id: UUID , text: str, notifyTime: datetime, ChatIDs: list[int], event: Event, **kwargs):
        self.Event = event
        super().__init__(id, text, notifyTime, ChatIDs, **kwargs)

    def GetMessageText(self) -> str:
        msg = f"Уведомление о назначении на событие \"{self.Event.Name}\", " + \
            f"которое пройдет {self.Event.Date} в {self.Event.Place}\n{self.Text}"
        return msg

    def __str__(self):
        return f"AssignmentNotif(id={str(self.ID)[:4]}, text={self.Text[:7]}, chats={self.ChatIDs}, time={self.NotifyTime}, event={self.Event.Name})"

class EventRemoveNotif(BaseNotifWithEvent):
    TYPE = TypeNotif.EVENT_REMOVE

    def __init__(self, id: UUID , text: str, notifyTime: datetime, ChatIDs: list[int], event: Event, **kwargs):
        self.Event = event
        super().__init__(id, text, notifyTime, ChatIDs, **kwargs)

    def GetMessageText(self) -> str:
        msg = f"Уведомление об отмене мепрориятия \"{self.Event.Name}\" \n{self.Text}"
        return msg
    
    def __str__(self):
        return f"EventRemoveNotif(id={str(self.ID)[:4]}, text={self.Text[:7]}, chats={self.ChatIDs}, time={self.NotifyTime}, event={self.Event.Name})"


class InfoNotif(BaseNotification):
    TYPE = TypeNotif.INFO

    def __init__(self, id: UUID , text: str, notifyTime: datetime, ChatIDs: list[int], **kwargs):
        super().__init__(id, text, notifyTime, ChatIDs, **kwargs)

    def GetMessageText(self) -> str:
        return self.Text
    
    def GetEventID(self) -> UUID:
        return None
    
    def __str__(self):
        return f"InfoNotif(id={str(self.ID)[:4]}, text={self.Text[:15]}, chats={self.ChatIDs}, time={self.NotifyTime})"
    

