

class ExportEventReportsRequest:
    def __init__(self, eventId: str, callback: Callable[[dict], None], args: list, kwargs: dict):
        if not isinstance(eventId, str):
            raise ValueError("eventId must be a string")
        
        if not callable(callback):
            raise ValueError("callback must be a callable")
        
        self._eventId = eventId
        self._callback = callback
        self._args = args
        self._kwargs = kwargs