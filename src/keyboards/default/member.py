from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup
from aiogram.types.keyboard_button import KeyboardButton

class MemberDefaultKeyboard:
    MakeReportButtonText = "Составить отчёт"
    EventInfoButtonText = "Инфа о меро"
    ListOfMeroButtonText = "Список моих меро"

    @staticmethod
    def Сreate():
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=__class__.MakeReportButtonText)],
                [KeyboardButton(text=__class__.EventInfoButtonText)]
                [KeyboardButton(text=__class__.ListOfMeroButtonText)]
            ],
            resize_keyboard=True,
            one_time_keyboard=False
        )