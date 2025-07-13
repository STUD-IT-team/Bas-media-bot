# Клавиатура отмены ввода ссылки при создании отчёта о мероприятии. 
# Используется в ручке MemberAddReport, в состоянии EnteringLink.

from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup

from keyboards.report_adding.cancel_button import CancelButton


class CancelLinkKeyboard:
    @staticmethod
    def Create() -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            keyboard=[
                [CancelButton.Create()]
            ],
            is_persistent=True,
            resize_keyboard=True,
            one_time_keyboard=False
        )
