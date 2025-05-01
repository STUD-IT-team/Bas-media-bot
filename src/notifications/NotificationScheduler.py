from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import asyncio
from typing import List, Dict, Optional
import uuid
from aiogram import Bot
from uuid import UUID

from models.notification import BaseNotification
# from models.notification import Notification


class NotificationScheduler:
    def __init__(self, bot: Optional[Bot]):
        self.scheduler = AsyncIOScheduler()
        self.bot = bot
        self.notifications: Dict[UUID, BaseNotification] = {}
        # self.notifications: Dict[str, Dict] = {}  # {id: {"text": str, "time": datetime}}
        
    async def AddNotification(self, notif: BaseNotification):
        """Добавляет уведомление и планирует его вывод"""
        self.notifications[notif.ID] = notif
        # notification_id = str(uuid.uuid4())
        # self.notifications[notification_id] = {
        #     "chat_id": chat_id,
        #     "text": text,
        #     "time": notify_time
        # }
        
        # Планируем задачу
        self.scheduler.add_job(
            self._sendNotification,
            'date',
            run_date=notif.NotifyTime,
            args=(notif.ID,),
            id=notif.ID.hex
        )
        
        # return notification_id
    
    async def _sendNotification(self, notification_id: UUID):
        """Внутренний метод для отправки уведомления"""
        if notification_id in self.notifications:
            notification = self.notifications.pop(notification_id)
            if self.bot:
                await self.bot.send_message(
                    chat_id=notification.ChatID,
                    text=notification.GetMessageText()
                )
    
    async def Start(self):
        """Запускает планировщик"""
        self.scheduler.start()
        print("Сервис уведомлений запущен. Ожидание запланированных сообщений...")
        try:
            while True:
                await asyncio.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            self.scheduler.shutdown()
            print("Сервис уведомлений остановлен.")
    
    # async def cancel_notification(self, notification_id: str) -> bool:
    #     """Отменяет запланированное уведомление"""
    #     if notification_id in self.notifications:
    #         self.scheduler.remove_job(notification_id)
    #         self.notifications.pop(notification_id)
    #         return True
    #     return False
    
