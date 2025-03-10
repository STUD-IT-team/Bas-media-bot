from aiogram import BaseMiddleware
from storage.storage import BaseStorage
from collections.abc import Callable, Awaitable
from aiogram.types import Update, Message
from typing import Dict, Any
from logging import Logger
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove


from keyboards.telegram.personal_data import PersonalDataAgreementKeyboard
from models.telegram import TelegramUserAgreement


class AgreementMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        if not 'storage' in data:
            raise ValueError("AgreementMiddleware: Storage middleware used in auth middleware")
        storage = data['storage']
        if not isinstance(storage, BaseStorage):
            raise ValueError("AgreementMiddleware: Storage middleware used with non-storage object")
        logger = data['logger']
        if not isinstance(logger, Logger):
            raise ValueError("AgreementMiddleware: Logger must be instance of Logger")

        mess = event.message
        agreement = storage.GetTelegramUserPersonalDataAgreement(mess.chat.id)
        logger.info(f"Agreement {agreement}")
        if agreement is not None and agreement.Agreed:
            return await handler(event, data)
        elif (agreement is None or not agreement.Agreed) and mess.text == PersonalDataAgreementKeyboard.AgreeButtonText:
            agreement = TelegramUserAgreement(
                ChatID=mess.chat.id,
                Username=mess.chat.username,
                Agreed=True,
            )
            storage.SetTelegramUserPersonalDataAgreement(agreement)
            await mess.answer("Спасибо за согласие! Теперь вы можете использовать бота", reply_markup=ReplyKeyboardRemove())
            return await handler(event, data)
        else:
            await mess.answer("Для использования бота вы должны согласиться на сбор и обработку ваших персональных данных согласно закону 152-ФЗ", reply_markup=PersonalDataAgreementKeyboard.Create())
