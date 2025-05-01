from uuid import UUID
from datetime import datetime

from models.event import Event

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
    
    