from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup
from aiogram.types.keyboard_button import KeyboardButton
from keyboards.confirmation.cancel import CancelKeyboard
from models.activist import Activist, TgUserActivist
from uuid import UUID


class MemberChoosingKeyboard:
    CancelButtonText = "Отмена"

    def __init__(self, activists: list[TgUserActivist]):
        if not isinstance(activists, list):
            raise ValueError('activists must be a list')
        for act in activists:
            if not isinstance(act, TgUserActivist):
                raise ValueError('activists must contain instances of Activist')

        self.activists = activists
    def Create(self) -> ReplyKeyboardMarkup:
        buttons = []
        for act in self.activists:
            buttons.append([KeyboardButton(text=f"{act.Name} ( @{act.Username} )")])
        buttons.append([KeyboardButton(text=__class__.CancelButtonText)])
        return ReplyKeyboardMarkup(
            keyboard=buttons,
            resize_keyboard=True,
            one_time_keyboard=False
        )


class MemberChoosingCancelKeyboard:
    StopActivistChoosingButtonText = 'Закончить выбор активистов'
    def __init__(self, activists: list[Activist]):
        if not isinstance(activists, list):
            raise ValueError('activists must be a list')
        for act in activists:
            if not isinstance(act, Activist):
                raise ValueError('activists must contain instances of Activist')

        self.activists = activists

    def Create(self) -> ReplyKeyboardMarkup:
        buttons = []
        for act in self.activists:
            buttons.append([KeyboardButton(text=act.Name)])
        buttons.append([KeyboardButton(text=__class__.StopActivistChoosingButtonText)])
        buttons.append([KeyboardButton(text=CancelKeyboard.CancelButtonText)])
        return ReplyKeyboardMarkup(
            keyboard=buttons,
            resize_keyboard=True,
            one_time_keyboard=False
        )
