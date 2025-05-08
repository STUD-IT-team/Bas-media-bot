from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup
from aiogram.types.keyboard_button import KeyboardButton

class PersonalDataAgreementKeyboard:
    AgreeButtonText = "✅ Я согласен"

    @staticmethod
    def Create():
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=__class__.AgreeButtonText)],
            ],
            resize_keyboard=True,
            one_time_keyboard=False
        )
