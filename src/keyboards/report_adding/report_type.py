# Клавиатура выбора типа отчёта, в ручке MemberAddReport, используется в состоянии ChosingType.

from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup
from aiogram.types.keyboard_button import KeyboardButton

from keyboards.report_adding.cancel_button import CancelButton


class ReportTypeKeyboard:
    PhotoButtonText = "Фото"
    VideoButtonText = "Видео"

    @staticmethod
    def Create() -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=__class__.PhotoButtonText), KeyboardButton(text=__class__.VideoButtonText)],
                [CancelButton.Create()]
            ],
            is_persistent=True,
            resize_keyboard=True,
            one_time_keyboard=False
        )
