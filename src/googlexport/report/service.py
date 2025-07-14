from googlexport.api.client import GoogleServiceClient
from googlexport.report.repository import ExporterRepository
from googlexport.api.spreadsheet import GoogleSpreadsheet

from queue import Queue, Empty

import asyncio

class ExportService:
    def __init__(self, googleAcc: GoogleServiceClient, spreadsheetId: str, storage: ExporterRepository):
        if not isinstance(googleAcc, GoogleServiceClient):
            raise ValueError("googleAcc must be an instance of GoogleServiceClient")
        
        if not isinstance(spreadsheetId, str):
            raise ValueError("spreadsheetId must be a string")
        
        if not issubclass(storage, ExporterRepository):
            raise ValueError("storage must be an instance of ExporterRepository")
        
        self._googleAcc = googleAcc
        self._spreadsheetId = spreadsheetId
        self._storage = storage
        self._spreadsheet = GoogleSpreadsheet(self._googleAcc, self._spreadsheetId)

        self._exportRequests = Queue()
        self._jobEvent = asyncio.Event()
    
    async def AddExportRequest(self, request: ExportEventReportsRequest):
        if not isinstance(request, ExportEventReportsRequest):
            raise ValueError("request must be an instance of ExportEventReportsRequest")
        
        self._exportRequests.put(request)
        self._startJob()
    
    async def _startJob(self):
        self._jobEvent.set()
    
    async def _mainCycle(self):
        while True:
            await self._jobEvent.wait()
            try:
                request = self._exportRequests.get_nowait()
            except Empty:
                self._jobEvent.clear()
                continue
            
            exportException = None
            try:
                await self._exportEvent(request._eventId)
            except Exception as e:
                exportException = e
            kwargs = request._kwargs.copy()
            kwargs['exception'] = exportException

            await self._taskDone(request._callback, request._args, kwargs)

    async def _exportEvent(self, eventId: str):
        event = self._storage.GetEvent(eventId)
        if event is None:
            raise ValueError(f"Event with id {eventId} does not exist")
        
    async def _taskDone(self, callback: Callable[[dict], None], args: list, kwargs: dict):
        await callback(*args, **kwargs)
    
    async def Start(self):
        self._jobEvent.clear()
        self._exportRequest = Queue()
        await self._mainCycle()
    

    