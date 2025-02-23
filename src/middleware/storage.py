from aiogram import BaseMiddleware
from storage.storage import BaseStorage
from collections.abc import Callable, Awaitable
from aiogram.types import Message
from typing import Dict, Any


class StorageMiddleware(BaseMiddleware):
    def __init__(self, storageClass: Callable[..., BaseStorage], *args, **kwargs):
        self.storageClass = storageClass
        self.kwargs = kwargs
        self.args = args
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        data['storage'] = self.storageClass(*self.args, **self.kwargs)
        return await handler(event, data)
