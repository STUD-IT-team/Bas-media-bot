from typing import Callable
from uuid import UUID

class ExportEventReportsRequest:
    def __init__(self, eventId: UUID, callback: Callable[[dict], None], args: list, kwargs: dict):
        if not isinstance(eventId, UUID):
            raise ValueError("eventId must be a UUID")
        
        if not callable(callback):
            raise ValueError("callback must be a callable")
        
        self._eventId = eventId
        self._callback = callback
        self._args = args
        self._kwargs = kwargs