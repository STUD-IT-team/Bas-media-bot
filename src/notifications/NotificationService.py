import uuid
from aiogram import Bot
from typing import List, Dict, Optional
from collections.abc import Callable
from datetime import datetime

from storage.storage import BaseStorage
from notifications.NotificationScheduler import NotificationScheduler
from models.notification import Notification, NotifType

class NotificationService:
    def __init__(self, bot: Optional[Bot]):
        self.notifScheduler = NotificationScheduler(bot)
        self.storage = None

    async def AddStorage(self, storage: Optional[BaseStorage]):
        self.storage = storage
        # TODO заполнить  self.notifScheduler данными из БД

        n1 = Notification(
            ID=uuid.uuid4(), 
            Text="Пора пить кофе!", 
            NotifyTime=datetime.now().replace(second=datetime.now().second + 5),
            Type=NotifType.REQUEST,
            ChatID=937944297,
            EventID=uuid.UUID(int=0)
        )
        n2 = Notification(
            ID=uuid.uuid4(), 
            Text="Проверить почту", 
            NotifyTime=datetime.now().replace(second=datetime.now().second + 5),
            Type=NotifType.REMINDER,
            ChatID=937944297,
            EventID=uuid.UUID(int=0)
        )
        await self.AddNotification(n1)
        await self.AddNotification(n2)
    
    async def AddNotification(self, notif: Notification):
        if not self.storage is None:
            pass # TODO add note

        await self.notifScheduler.AddNotification(notif)

    async def StartScheduler(self):
        await self.notifScheduler.Start()

    