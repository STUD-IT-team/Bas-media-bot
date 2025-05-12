from uuid import UUID
from models.notification import \
    BaseNotification, BaseNotifWithEvent, TypeNotif


class BaseFilterNotif:
    def filter(self, notif: BaseNotification) -> bool:
        raise NotImplementedError
    
class EventFilter(BaseFilterNotif):
    def __init__(self, eventID: UUID):
        self.eventID = eventID
        super().__init__()

    def filter(self, notif: BaseNotification) -> bool:
        return isinstance(notif, BaseNotifWithEvent) and notif.GetEventID() == self.eventID
    
class TypeFilter(BaseFilterNotif):
    def __init__(self, type: TypeNotif):
        self.type = type
        super().__init__()

    def filter(self, notif: BaseNotification) -> bool:
        return notif.__class__.TYPE == self.type




