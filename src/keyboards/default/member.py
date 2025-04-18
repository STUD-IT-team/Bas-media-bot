from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup
from aiogram.types.keyboard_button import KeyboardButton

class MemberDefaultKeyboard:
    MakeReportButtonText = "Составить отчёт"
    EventInfoButtonText = "Инфа о меро"

    @staticmethod
    def Create():
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=__class__.MakeReportButtonText)],
                [KeyboardButton(text=__class__.EventInfoButtonText)]
            ],
            resize_keyboard=True,
            one_time_keyboard=False
        )