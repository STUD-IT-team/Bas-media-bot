# Клавиатура выбора мероприятия при создании отчёта. 
# Используется в ручке MemberAddReport, в состоянии ChosingEvents.

from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup
from aiogram.types.keyboard_button import KeyboardButton

from keyboards.report_adding.cancel_button import CancelButton

from models.event import EventForActivist


class ActivistEventsKeyboard:
    def __init__(self, events: list[EventForActivist]):
        if not isinstance(events, list):
            raise ValueError("events must be list")

        if not all(isinstance(event, EventForActivist) for event in events):
            raise ValueError(f"events list must contain only instances of EventForActivist")

        # Отсортированы по алфавиту.
        self.eventButtonTexts = sorted([event.Name for event in events])

    def Create(self) -> ReplyKeyboardMarkup:
        buttons = [[KeyboardButton(text=eventButtonText)] for eventButtonText in self.eventButtonTexts]
        buttons.append([CancelButton.Create()])
        
        return ReplyKeyboardMarkup(
            keyboard=buttons,
            is_persistent=True,
            resize_keyboard=True,
            one_time_keyboard=False
        )
