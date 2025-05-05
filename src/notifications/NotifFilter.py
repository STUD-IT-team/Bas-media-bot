from uuid import UUID
from models.notification import \
    BaseNotification, MapperNotification, BaseNotifWithEvent, TypeNotif


class BaseFilterNotif:
    def filter(self, notif: BaseNotification) -> bool:
        raise NotImplementedError
    
class EventFilter(BaseFilterNotif):
    def __init__(self, eventID: UUID):
        self.eventID = eventID
        super().__init__()

    def filter(self, notif: BaseNotification) -> bool:
        if not isinstance(notif, BaseNotifWithEvent):
            return False
        return notif.GetEventID() == self.eventID
    
class TypeFilter(BaseFilterNotif):
    def __init__(self, type: TypeNotif):
        self.type = type
        super().__init__()

    def filter(self, notif: BaseNotification) -> bool:
        return notif.__class__.__name__ == MapperNotification.GetClassNameByType(self.type)




