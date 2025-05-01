from uuid import UUID
from typing import cast
from models.notification import BaseNotification, MapperNotification



class FilterNotif:
    @classmethod
    def TypeFilter(cls, notif: BaseNotification, type: str) -> bool:
        return notif.__class__.__name__ == MapperNotification.GetClassNameByType(type)

    @classmethod
    def EventFilter(cls, notif: BaseNotification, eventID: UUID) -> bool:
        if not notif.RelatedToEvent():
            return False
        return notif.GetEventID() == eventID



