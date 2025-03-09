from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup
from aiogram.types.keyboard_button import KeyboardButton
from models.activist import Activist
from uuid import UUID

class MemberChoosingKeyboard:
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
        return ReplyKeyboardMarkup(
            keyboard=buttons,
            resize_keyboard=True,
            one_time_keyboard=False
        )

class MemberChoosingCancelKeyboard:
    StopActivistChoosingButtonText = 'Закончить выбор активистов'
    def __init__(self, activists: list[Activist], exceptIDs: list[UUID] = []):
        if not isinstance(activists, list):
            raise ValueError('activists must be a list')
        for act in activists:
            if not isinstance(act, Activist):
                raise ValueError('activists must contain instances of Activist')

        self.activists = activists

        if not isinstance(exceptIDs, list):
            raise ValueError('exceptIDs must be a list')
        for exc in exceptIDs:
            if not isinstance(exc, UUID):
                raise ValueError('exceptIDs must contain instances of UUID')

        self.exceptIDs = exceptIDs

    def Create(self) -> ReplyKeyboardMarkup:
        buttons = []
        for act in self.activists:
            if act.ID not in self.exceptIDs:
                buttons.append([KeyboardButton(text=act.Name)])
        buttons.append([KeyboardButton(text=__class__.StopActivistChoosingButtonText)])
        return ReplyKeyboardMarkup(
            keyboard=buttons,
            resize_keyboard=True,
            one_time_keyboard=False
        )