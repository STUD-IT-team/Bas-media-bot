from aiogram.types import Message
from aiogram import Router, F
from handlers.state import MemberReportAddingStates
from storage.storage import BaseStorage
from utils.strings import NewlineJoin
from aiogram.fsm.context import FSMContext
from handlers.usertransition import TransitToMemberDefault

from keyboards.events.activeevents import ActiveEventsKeyboard

MemberReportAddingRouter = Router()


async def TransitToMemberReportAdding(message : Message, storage : BaseStorage, state : FSMContext, logger : Logger):
    await state.set_state(MemberReportAddingStates.ChoosingEvent)
    activeEvents = storage.GetActiveEvents() # Добавить try except
    await message.answer("По какому мероприятию?", reply_markup=ActiveEventsKeyboard(activeEvents).Create())

@MemberReportAddingRouter.message(
    MemberReportAddingStates(),
    F.text == ActiveEventsKeyboard.CancelOperationButtonText
)
async def MemberCancelReportAdding(message: Message, storage: BaseStorage, state: FSMContext, logger: Logger):
    await TransitToMemberDefault(message, state, activist) # Активиста тонет