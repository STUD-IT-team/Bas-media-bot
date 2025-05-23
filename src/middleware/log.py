from aiogram import BaseMiddleware
from storage.storage import BaseStorage
from collections.abc import Callable, Awaitable
from aiogram.types import Update, Message
from typing import Dict, Any
from logging import Logger
from traceback import format_tb
from utils.strings import JoinStringsAddBorder

class LogMiddleware(BaseMiddleware):
    def __init__(self, logger=Logger):
        if (not isinstance(logger, Logger)):
            raise ValueError("logger must be an instance of Logger")
        self.logger = logger
        
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        data['logger'] = self.logger
        self.logger.info(f"Got new from {event.message.chat.id}:{event.message.chat.username}. Text: {event.message.text}")
        result = None
        try:
            result = await handler(event, data)
        except Exception as e:
            self.logger.error(f"LogMiddleware: Error: {e}\nTraceback:\n{JoinStringsAddBorder(format_tb(e.__traceback__))}End of traceback")
        self.logger.info(f"Processed {event.message.chat.id}:{event.message.chat.username}. Text: {event.message.text}")
        return result
