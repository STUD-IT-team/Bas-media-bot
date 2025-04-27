from aiogram import BaseMiddleware
from typing import Dict, Any, Callable, Awaitable
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from notifications.NotificationScheduler import NotificationScheduler

class NotifSchedulerMiddleware(BaseMiddleware):
    def __init__(self, notifScheduler: NotificationScheduler):
        if (not isinstance(notifScheduler, NotificationScheduler)):
            raise ValueError("notification Scheduler must be an instance of NotificationScheduler")
        self.notifScheduler = notifScheduler

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any]
    ) -> Any:
        data["notifScheduler"] = self.notifScheduler  # Добавляем планировщик в контекст
        return await handler(event, data)