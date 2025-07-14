from googlexport.report.service import ExportService
from googlexport.report.repository import PostgresRepository, PostgresCredentials
from googlexport.api.client import GoogleServiceClient
from typing import Callable

import asyncio

class NotInitializedError(Exception):
    pass

class Singleton:
    def __init__(self):
        self._instance = None
        self._lock = asyncio.Lock()
    
    async def __call__(self, *args, **kwargs):
        if self._instance is None:
            async with self._lock:
                if self._instance is None and len(args) == len(kwargs) == 0:
                    raise NotInitializedError("Instance is not initialized")
                if self._instance is None:
                    self._instance = await self._init(*args, **kwargs)
        return self._instance
    
    async def _init(self, *args, **kwargs):
        raise NotImplementedError

class SingletonExportService(Singleton):
    async def _init(self, serviceAccCredsFile: str, spreadsheetId: str, pgcred: PostgresCredentials):
        serviceAcc = GoogleServiceClient(serviceAccCredsFile)
        storage = PostgresRepository(pgcred)
        return ExportService(serviceAcc, spreadsheetId, storage)
    
_singletonExportService = SingletonExportService()

async def __init__(serviceAccCredsFile: str, spreadsheetId: str, pgcred: PostgresCredentials):
    return await _singletonExportService(serviceAccCredsFile, spreadsheetId, pgcred)

async def AddExportEventRequest(eventId: str, callback: Callable[[dict], None], args: list, kwargs: dict):
    return await _singletonExportService().AddExportRequest(ExportEventReportsRequest(eventId, callback, args, kwargs))



