from uuid import UUID
from models.notification import BaseNotification, MapperNotification


class BaseFilterNotif:
    def filter(self, notif: BaseNotification) -> bool:
        return True
    
class EventFilter(BaseFilterNotif):
    def __init__(self, eventID: UUID):
        self.eventID = eventID
        super().__init__()

    def filter(self, notif: BaseNotification) -> bool:
        if not notif.RelatedToEvent():
            return False
        return notif.GetEventID() == self.eventID
    
class TypeFilter(BaseFilterNotif):
    def __init__(self, type: str):
        self.type = type
        super().__init__()

    def filter(self, notif: BaseNotification) -> bool:
        return notif.__class__.__name__ == MapperNotification.GetClassNameByType(self.type)




