# Универсальная кнопка отмены используемая в клавиатурах ручки MemberAddReport.

from aiogram.types.keyboard_button import KeyboardButton


class CancelButton:
    CancelButtonText = "Отмена"
    
    @staticmethod
    def Create() -> KeyboardButton:
        return KeyboardButton(text=__class__.CancelButtonText)
