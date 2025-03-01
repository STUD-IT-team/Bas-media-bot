from aiogram import BaseMiddleware
from storage.storage import BaseStorage
from collections.abc import Callable, Awaitable
from aiogram.types import Message
from typing import Dict, Any
from logging import Logger


class LogMiddleware(BaseMiddleware):
    def __init__(self, logger=Logger):
        if (not isinstance(logger, Logger)):
            raise ValueError("logger must be an instance of Logger")
        self.logger = logger
        
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        data['logger'] = self.logger
        self.logger.info(f"Got new from {event.chat_id}:{event.chat.username}. Text: {event.text}")
        result = await handler(event, data)
        self.logger.info(f"Processed {event.chat_id}:{event.chat.username}. Text: {event.text}")
        return result

