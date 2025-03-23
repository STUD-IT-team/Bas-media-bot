from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup
from aiogram.types.keyboard_button import KeyboardButton

class AdminDefaultKeyboard:
    AddEventButtonText = "Добавить мероприятие"
    InfoEventButtonText = "Инфа о меро"
    CancelEventButtonText = "Отменить мероприятие"
    CompleteEventButtonText = "Завершить мероприятие"
    ExportButtonText = "Экспорт меро"
    AddMemberButtonText = "Добавить пользователя"
    DeleteMemberButtonText = "Удалить пользователя"
    BroadcastButtonText = "Массовая рассылка"

    @staticmethod
    def Create():
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=__class__.AddEventButtonText)],
                [KeyboardButton(text=__class__.InfoEventButtonText)],
                [KeyboardButton(text=__class__.CancelEventButtonText)],
                [KeyboardButton(text=__class__.CompleteEventButtonText)],
                [KeyboardButton(text=__class__.AddMemberButtonText)],
                [KeyboardButton(text=__class__.DeleteMemberButtonText)],
                [KeyboardButton(text=__class__.BroadcastButtonText)],
                [KeyboardButton(text=__class__.ExportButtonText)]
            ],
            resize_keyboard=True,
            one_time_keyboard=False
        )
    

class CancelAddMemberKeyboard:
    CancelAddMemberButtonText = "Отмена"

    @staticmethod
    def Create():
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=__class__.CancelAddMemberButtonText)],
            ],
            resize_keyboard=True,
            one_time_keyboard=False
        )
