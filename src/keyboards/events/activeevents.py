from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup
from aiogram.types.keyboard_button import KeyboardButton

class ActiveEventsKeyboard:
    CancelOperationButtonText = "Отмена операции"

    def __init__(self, events):
        self.events = events


    def Create(self):
        buttons = [[KeyboardButton(text=event.Name)] for event in self.events]
        buttons.append([KeyboardButton(text=self.CancelOperationButtonText)])
        
        return ReplyKeyboardMarkup(
            keyboard=buttons,
            resize_keyboard=True,
            one_time_keyboard=True
        )
