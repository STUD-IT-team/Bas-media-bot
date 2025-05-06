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
    NOTIF_REGISTRY = {}

    def __new__(cls, name, bases, atrs):
        new_cls = type.__new__(cls, name, bases, atrs)
        cls.NOTIF_REGISTRY[new_cls.__name__.lower()] = new_cls
        return new_cls

    @classmethod
    def get_notif_registry(cls):
        return dict(cls.NOTIF_REGISTRY)
    
    @classmethod
    def GetClassByName(cls, name):
        return cls.NOTIF_REGISTRY[name.lower()]

class MapperNotification:
    __mapClsNmType = {
        'EventReminderNotif': TypeNotif.EVENT_REMINDER,
        'InfoNotif': TypeNotif.INFO,
        'AssignmentNotif': TypeNotif.ASSIGNMENT,
        'EventRemoveNotif': TypeNotif.EVENT_REMOVE
        
    }
    __mapTypeClsNm = {v: k for k, v in __mapClsNmType.items()}

    @classmethod
    def GetClassNameByType(cls, type: TypeNotif) -> str:
        return cls.__mapTypeClsNm[type]
    
    @classmethod
    def GetTypeByClassName(cls, clsName: str) -> str:
        return cls.__mapClsNmType[clsName]

    @classmethod
    def GetClassByType(cls, type: TypeNotif) -> BaseNotification:
        notifClassName = cls.GetClassNameByType(type)
        return NotifRegistryBase.GetClassByName(notifClassName)
    
    @classmethod
    def CreateNotification(cls, type: TypeNotif, *args) -> BaseNotification:
        notifClassName = cls.GetClassNameByType(type)
        notifClass = NotifRegistryBase.GetClassByName(notifClassName)
        return notifClass(*args)


class BaseNotification(metaclass=NotifRegistryBase):
    def __init__(self, id: UUID , text: str, notifyTime: datetime, ChatIDs: list[int]):
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
    def GetEventID(self) -> UUID:
        return self.Event.ID


class EventReminderNotif(BaseNotifWithEvent):
    def __init__(self, id: UUID , text: str, notifyTime: datetime, ChatIDs: list[int], event: Event):
        self.Event = event
        super().__init__(id, text, notifyTime, ChatIDs)

    def GetMessageText(self) -> str:
        msg = f"🔔 Напоминание о событии \"{self.Event.Name}\", " + \
            f"которое пройдет {self.Event.Date} в {self.Event.Place}\n{self.Text}"
        return msg
    
    def __str__(self):
        return f"EventReminderNotif(id={str(self.ID)[:4]}, text={self.Text[:7]}, chats={self.ChatIDs}, time={self.NotifyTime}, event={self.Event.Name})"
    
class AssignmentNotif(BaseNotifWithEvent):
    def __init__(self, id: UUID , text: str, notifyTime: datetime, ChatIDs: list[int], event: Event):
        self.Event = event
        super().__init__(id, text, notifyTime, ChatIDs)

    def GetMessageText(self) -> str:
        msg = f"Уведомление о назначении на событие \"{self.Event.Name}\", " + \
            f"которое пройдет {self.Event.Date} в {self.Event.Place}\n{self.Text}"
        return msg

    def __str__(self):
        return f"AssignmentNotif(id={str(self.ID)[:4]}, text={self.Text[:7]}, chats={self.ChatIDs}, time={self.NotifyTime}, event={self.Event.Name})"

class EventRemoveNotif(BaseNotifWithEvent):
    def __init__(self, id: UUID , text: str, notifyTime: datetime, ChatIDs: list[int], event: Event):
        self.Event = event
        super().__init__(id, text, notifyTime, ChatIDs)

    def GetMessageText(self) -> str:
        msg = f"Уведомление об отмене мепрориятия \"{self.Event.Name}\" \n{self.Text}"
        return msg
    
    def __str__(self):
        return f"EventRemoveNotif(id={str(self.ID)[:4]}, text={self.Text[:7]}, chats={self.ChatIDs}, time={self.NotifyTime}, event={self.Event.Name})"


class InfoNotif(BaseNotification):
    def __init__(self, id: UUID , text: str, notifyTime: datetime, ChatIDs: list[int]):
        super().__init__(id, text, notifyTime, ChatIDs)

    def GetMessageText(self) -> str:
        return self.Text
    
    def GetEventID(self) -> UUID:
        return None
    
    def __str__(self):
        return f"InfoNotif(id={str(self.ID)[:4]}, text={self.Text[:15]}, chats={self.ChatIDs}, time={self.NotifyTime})"
    

