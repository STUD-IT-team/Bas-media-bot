from aiogram import Bot
from typing import Optional
from uuid import UUID

from storage.storage import BaseStorage
from notifications.NotificationScheduler import NotificationScheduler
from models.notification import BaseNotification
from notifications.NotifFilter import BaseFilterNotif


class NotificationService:
    def __init__(self, bot: Optional[Bot]):
        self.notifScheduler = NotificationScheduler(bot, self.SetDoneNotifications)
        self.storage = None

    async def AddStorage(self, storage: Optional[BaseStorage]):
        self.storage = storage
        notifications = storage.GetAllNotDoneNotifs()
        for n in notifications:
            await self.notifScheduler.AddNotification(n)
    
    async def AddNotification(self, notif: BaseNotification):
        if self.storage is not None:
            self.storage.PutNotification(notif)
        await self.notifScheduler.AddNotification(notif)

    async def RemoveNotifications(self, filter: BaseFilterNotif):
        if self.storage is not None:
            removed = await self.notifScheduler.RemoveNotifications(filter)
            for n in removed:
                self.storage.RemoveNotification(n.ID)

    async def SetDoneNotifications(self, notifID: UUID):
        if self.storage is not None:
            self.storage.SetDoneNotification(notifID)

    async def StartScheduler(self):
        await self.notifScheduler.Start()

    