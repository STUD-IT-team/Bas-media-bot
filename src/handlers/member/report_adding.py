from aiogram import Router, F
from aiogram.types import Message
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from logging import Logger
from storage.storage import BaseStorage

# Переход в дефолтную стейт машину:
from handlers.usertransition import TransitToMemberDefault, TransitToUnauthorized

# Стейты:
from handlers.state import MemberReportAddingStates

# Клавиатуры и кнопки:
from keyboards.report_adding.cancel_button import CancelButton
from keyboards.report_adding.activist_events import ActivistEventsKeyboard
from keyboards.report_adding.cancel_link import CancelLinkKeyboard
from keyboards.report_adding.report_type import ReportTypeKeyboard
from keyboards.report_adding.report_confirm import ReportConfirmKeyboard

MemberReportAddingRouter = Router()


# Ручка перехода в составление отчёта
async def TransitToMemberReportAdding(message: Message, storage: BaseStorage, state: FSMContext, logger: Logger) -> None:
    await state.set_state(MemberReportAddingStates.ChoosingEvent)

    try:
        activist = storage.GetActivistByChatID(message.chat.id)
    except:
        message.answer("Ошибка получения информации о вашей роли.")
        raise

    if activist is None:
        logger.warning(f"User {str(message.chat.id)} became unauthorized.")
        await TransitToUnauthorized(message=message, state=state)
        return

    # WARNING: вероятно нужно написать функцию GetActiveEventsByActivistID.
    try:
        activistEvents = storage.GetEventsByActivistID(activist.ID)
        activistEventsKeyboard = ActivistEventsKeyboard(activistEvents)
    except:
        message.answer("Ошибка при получении информации о ваших мероприятиях.")
        raise

    await message.answer("Выберите мероприятие для составления отчёта:", \
            reply_markup=activistEventsKeyboard.Create())
    
    return


# Отмена составления отчёта
@MemberReportAddingRouter.message(
    MemberReportAddingStates(),
    F.text == CancelButton.CancelButtonText
)
async def CancelReportAdding(message: Message, storage: BaseStorage, state: FSMContext) -> None:
    await message.answer("Создание отчёта отменено.", reply_markup=ReplyKeyboardRemove())
    
    try:
        activist = storage.GetActivistByChatID(message.chat.id)
    except:
        message.answer("Ошибка получения информации о вашей роли.")
        raise

    if activist is None:
        logger.warning(f"User {str(message.chat.id)} became unauthorized.")
        await TransitToUnauthorized(message=message, state=state)
    else:
        await TransitToMemberDefault(message=message, state=state, activist=activist)
    
    return


# Не сработало ни одной ручки составления отчёта
@MemberReportAddingRouter.message(MemberReportAddingStates())
async def UnknownReportAdding(message: Message, storage: BaseStorage, state: FSMContext) -> None:
    await message.answer("Выбран несуществующий вариант ответа. Попробуйте ещё раз.")

    return


# Заметка самому себе:
# Убери код проверки авторизации, т.к. оно проверяется в AuthMiddleware