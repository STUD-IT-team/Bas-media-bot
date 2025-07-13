# Клавиатура подтверждения при отправке отчёта, в ручке MemberAddReport, используется в состоянии Confirmation.

from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup
from aiogram.types.keyboard_button import KeyboardButton

from keyboards.report_adding.cancel_button import CancelButton


class ReportConfirmKeyboard:
    ConfirmButtonText = "Всё верно"
    RetryButtonText = "Ввести заново"

    @staticmethod
    def Create() -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=__class__.ConfirmButtonText)],
                [KeyboardButton(text=__class__.RetryButtonText)],
                [CancelButton.Create()]
            ],
            is_persistent=True,
            resize_keyboard=True,
            one_time_keyboard=False
        )
