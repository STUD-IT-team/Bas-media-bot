from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup
from aiogram.types.keyboard_button import KeyboardButton

class YesNoKeyboard:
    YesButtonText = "Да"
    NoButtonText = "Нет"

    @staticmethod
    def Create():
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=__class__.YesButtonText)],
                [KeyboardButton(text=__class__.NoButtonText)],
            ],
            resize_keyboard=True,
            one_time_keyboard=False
        )
