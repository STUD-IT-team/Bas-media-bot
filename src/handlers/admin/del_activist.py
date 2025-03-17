from handlers.state import AdminMemberDeletingStates
from handlers.usertransition import TransitToAdminDefault
from aiogram import F
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from storage.storage import BaseStorage
from logging import Logger
from keyboards.activist.choosing import MemberChoosingKeyboard
from keyboards.default.admin import YesNoKeyboard
import re
from uuid import UUID

AdminDelMemberRouter = Router()

async def TransitToAdminDelMember(message : Message, storage : BaseStorage, state : FSMContext, logger : Logger):
    await state.set_state(AdminMemberDeletingStates.ChoosingMember)
    validTgUserActivists = storage.GetValidTgUserActivist()
    tmptext = "Выберити пользователя, которого собираетесь удалить"
    await message.answer(tmptext, reply_markup=MemberChoosingKeyboard(validTgUserActivists).Create())

@AdminDelMemberRouter.message(
    AdminMemberDeletingStates.ChoosingMember,
    F.text == MemberChoosingKeyboard.CancelButtonText
)
async def AdminCancelDelMember(message : Message, storage : BaseStorage, state : FSMContext, logger : Logger):
    act = storage.GetActivistByChatID(message.chat.id)
    await TransitToAdminDefault(message=message, state=state, activist=act)

@AdminDelMemberRouter.message(AdminMemberDeletingStates.ChoosingMember)
async def AdminChooseDelMember(message : Message, storage : BaseStorage, state : FSMContext, logger : Logger):
    await state.set_state(AdminMemberDeletingStates.ConfirmingDelMember)
    msg_username = re.search(r'@(\w+)', message.text)
    if not msg_username is None:
        validTgUserActivists = storage.GetValidTgUserActivist()
        for act in validTgUserActivists:
            if msg_username.group(1) == act.Username:
                if act.ChatID == message.chat.id:
                    await message.answer(f"Вы не можете удалить сами себя")
                    act = storage.GetActivistByChatID(message.chat.id)
                    await TransitToAdminDefault(message=message, state=state, activist=act)
                    return
                data = await state.get_data()
                data["id_ActToDel"] = str(act.IdActivist)
                data["name_ActToDel"] = act.Name
                data["username_ActToDel"] = act.Username
                await state.update_data(data)
                await message.answer(f"Выуверены что хотите удалить пользователя {act.Name} ( {act.Username} )?", 
                            reply_markup=YesNoKeyboard.Create())
                return 
    await message.answer(f"Пользователя с именем {message.text} нет в списках")
    act = storage.GetActivistByChatID(message.chat.id)
    await TransitToAdminDefault(message=message, state=state, activist=act)


@AdminDelMemberRouter.message(
    AdminMemberDeletingStates.ConfirmingDelMember,
    F.text == YesNoKeyboard.YesButtonText
)
async def AdminCancelAddMember(message : Message, storage : BaseStorage, state : FSMContext, logger : Logger):
    data = await state.get_data()
    storage.MakeInvalidActivist(UUID(data["id_ActToDel"]))
    await message.answer(f"Пользователь {data["name_ActToDel"]} ({data["username_ActToDel"]}) был удален")

    act = storage.GetActivistByChatID(message.chat.id)
    await TransitToAdminDefault(message=message, state=state, activist=act)

@AdminDelMemberRouter.message(
    AdminMemberDeletingStates.ConfirmingDelMember,
    F.text == YesNoKeyboard.NoButtonText
)
async def AdminCancelAddMember(message : Message, storage : BaseStorage, state : FSMContext, logger : Logger):
    await message.answer(f"Отмена операции")
    act = storage.GetActivistByChatID(message.chat.id)
    await TransitToAdminDefault(message=message, state=state, activist=act)

@AdminDelMemberRouter.message(AdminMemberDeletingStates.ConfirmingDelMember)
async def AdminCancelAddMember(message : Message, storage : BaseStorage, state : FSMContext, logger : Logger):
    await message.answer(f"Ответьте, пожалуйста да/нет")



