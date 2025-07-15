from googlexport.api.client import GoogleServiceClient
from googlexport.report.repository import ExporterRepository
from googlexport.api.spreadsheet.spreadsheet import GoogleSpreadsheet
from googlexport.report.requests import ExportEventReportsRequest
from googlexport.report.exporter import ReportExporter

from uuid import UUID

from logging import Logger

from queue import Queue, Empty
from typing import Callable

import asyncio
import threading

class ExportService:
    KwargsExceptionName = 'exception'
    KwargsSpreadsheetUrl = 'spreadsheetUrl'
    SleepSeconds = 2

    def __init__(self, googleAcc: GoogleServiceClient, spreadsheetId: str, storage: ExporterRepository, logger: Logger):
        if not isinstance(googleAcc, GoogleServiceClient):
            raise ValueError("googleAcc must be an instance of GoogleServiceClient")
        
        if not isinstance(spreadsheetId, str):
            raise ValueError("spreadsheetId must be a string")
        
        if not isinstance(storage, ExporterRepository):
            raise ValueError("storage must be an instance of ExporterRepository")
        
        self._googleAcc = googleAcc
        self._spreadsheetId = spreadsheetId
        self._storage = storage
        self._spreadsheet = GoogleSpreadsheet(self._googleAcc, self._spreadsheetId)
        self._logger = logger
        self._was_started = threading.Event()

        self._exportRequests = Queue()
    
    async def AddExportRequest(self, request: ExportEventReportsRequest):
        if not isinstance(request, ExportEventReportsRequest):
            raise ValueError("request must be an instance of ExportEventReportsRequest")
        
        self._exportRequests.put(request)
    
    async def Start(self):
        if self._was_started.is_set():
            raise ValueError("Service was already initialized")
        
        self._was_started.set()
        self._logger.info("Start export service")
        await self._mainCycle()
    
    # should be called from a separate thread/proccess as it will blocked on the queue
    async def _mainCycle(self):
        self._logger.info("Start main cycle")
        while True:
            # puts thread into uninterruptable sleep
            # should think about using other synchronization mechanism with queue
            request = self._exportRequests.get(block=True, timeout=None)
            exportException = None
            try:
                await self._exportEvent(request._eventId)
            except Exception as e:
                exportException = e

            await self._taskDone(request._callback, request._args, request._kwargs, e=exportException)

    async def _exportEvent(self, eventId: UUID):
        exporter = ReportExporter(self._spreadsheet, self._storage)
        await exporter.ExportEvent(eventId)
        
    async def _taskDone(self, callback: Callable[[dict], None], args: list, kwargs: dict, e : Exception = None):
        await callback(*args, **(await self._addKwargs(e, kwargs)))
    
    async def _addKwargs(self, e: Exception, kwargs: dict):
        kwargs['exception'] = e
        kwargs['spreadsheetUrl'] = self._spreadsheet.url
        return kwargs
    
   

    