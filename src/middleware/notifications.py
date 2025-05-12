from aiogram import BaseMiddleware
from typing import Dict, Any, Callable, Awaitable
from notifications.NotificationService import NotificationService

class NotificationsMiddleware(BaseMiddleware):
    def __init__(self, notifServ: NotificationService):
        if (not isinstance(notifServ, NotificationService)):
            raise ValueError("notification Scheduler must be an instance of NotificationService")
        self.notifServ = notifServ

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any]
    ) -> Any:
        data["notifServ"] = self.notifServ  # Добавляем планировщик в контекст
        return await handler(event, data)