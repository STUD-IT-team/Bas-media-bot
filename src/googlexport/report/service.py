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

        self._exportRequests = Queue()
        self._logger.info("Init export service")  
    
    async def AddExportRequest(self, request: ExportEventReportsRequest):
        if not isinstance(request, ExportEventReportsRequest):
            raise ValueError("request must be an instance of ExportEventReportsRequest")
        
        self._exportRequests.put(request)
    
    async def Start(self):
        self._logger.info("Start export service")
        self._exportRequest = Queue()
        await self._mainCycle()
    
    async def _mainCycle(self):
        self._logger.info("Start main cycle")
        while True:
            try:
                request = self._exportRequests.get_nowait()
            except Empty:
                await asyncio.sleep(self.SleepSeconds)
                continue
            
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
    
   

    