from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import asyncio
from typing import List, Dict, Optional
import uuid
from aiogram import Bot

class NotificationScheduler:
    def __init__(self, bot: Optional[Bot]):
        self.scheduler = AsyncIOScheduler()
        self.bot = bot
        self.notifications: Dict[str, Dict] = {}  # {id: {"text": str, "time": datetime}}
        
    async def add_notification(self, chat_id: int, text: str, notify_time: datetime) -> str:
        """Добавляет уведомление и планирует его вывод"""
        notification_id = str(uuid.uuid4())
        
        self.notifications[notification_id] = {
            "chat_id": chat_id,
            "text": text,
            "time": notify_time
        }
        
        # Планируем задачу
        self.scheduler.add_job(
            self._send_notification,
            'date',
            run_date=notify_time,
            args=(notification_id,),
            id=notification_id
        )
        
        return notification_id
    
    async def _send_notification(self, notification_id: str):
        """Внутренний метод для отправки уведомления"""
        if notification_id in self.notifications:
            notification = self.notifications.pop(notification_id)
            if self.bot:
                await self.bot.send_message(
                    chat_id=notification["chat_id"],
                    text=f"🔔 Уведомление:\n{notification['text']}"
                )

    # async def _print_notification(self, notification_id: str):
    #     """Внутренний метод для вывода уведомления"""
    #     if notification_id in self.notifications:
    #         notification = self.notifications.pop(notification_id)
    #         print(f"\n🔔 Уведомление [{notification['time'].strftime('%H:%M:%S')}]:")
    #         print(notification["text"])
    #         print("-" * 40)
    
    async def start(self):
        """Запускает планировщик"""
        self.scheduler.start()
        print("Сервис уведомлений запущен. Ожидание запланированных сообщений...")
        await self.add_notification(
            chat_id=937944297,
            text="Пора пить кофе!",
            notify_time=datetime.now().replace(second=datetime.now().second + 5)
        )
        await self.add_notification(
            937944297,
            "Проверить почту",
            datetime.now().replace(second=datetime.now().second + 10)
        )
        
        try:
            while True:
                await asyncio.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            self.scheduler.shutdown()
            print("Сервис уведомлений остановлен.")
    
    async def cancel_notification(self, notification_id: str) -> bool:
        """Отменяет запланированное уведомление"""
        if notification_id in self.notifications:
            self.scheduler.remove_job(notification_id)
            self.notifications.pop(notification_id)
            return True
        return False
    
    def get_pending_notifications(self) -> List[Dict]:
        """Возвращает список ожидающих уведомлений"""
        return [
            {"id": nid, **data} 
            for nid, data in self.notifications.items()
        ]

# Пример использования
async def main():
    notifier = NotificationScheduler()
    
    # Добавляем уведомления (текущее время + 5 и 10 секунд)
    await notifier.add_notification(
        chat_id=937944297,
        text="Пора пить кофе!",
        notify_time=datetime.now().replace(second=datetime.now().second + 5)
    )
    
    await notifier.add_notification(
        937944297,
        "Проверить почту",
        datetime.now().replace(second=datetime.now().second + 10)
    )
    
    print("Ожидающие уведомления:")
    for n in notifier.get_pending_notifications():
        print(f" - {n['text']} в {n['time'].strftime('%H:%M:%S')}")
    
    await notifier.start()

if __name__ == "__main__":
    asyncio.run(main())