from googlexport.report.service import ExportService
from googlexport.report.repository import PostgresRepository, PostgresCredentials
from googlexport.report.requests import ExportEventReportsRequest   
from googlexport.api.client import GoogleServiceClient
from logging import Logger
from typing import Callable

import asyncio
import threading

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

class SingletonThreadedExportService(Singleton):
    async def _init(self, serviceAccCredsFile: str, spreadsheetId: str, pgcred: PostgresCredentials, logger: Logger):
        serviceAcc = GoogleServiceClient(serviceAccCredsFile)
        storage = PostgresRepository(pgcred)
        serv = ExportService(serviceAcc, spreadsheetId, storage, logger)

        thread = threading.Thread(target=asyncio.run, args=(serv.Start(),))
        thread.start()

        return serv
        
_singletonExportService = SingletonThreadedExportService()

async def __init__(serviceAccCredsFile: str, spreadsheetId: str, pgcred: PostgresCredentials, logger: Logger):
    return await _singletonExportService(serviceAccCredsFile, spreadsheetId, pgcred, logger)

async def AddExportEventRequest(request: ExportEventReportsRequest):
    return await (await _singletonExportService()).AddExportRequest(request)



