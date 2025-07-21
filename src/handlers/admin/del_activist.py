from handlers.state import AdminMemberDeletingStates
from handlers.usertransition import TransitToAdminDefault
from aiogram import F
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from storage.storage import BaseStorage
from logging import Logger
from keyboards.activist.choosing import MemberChoosingKeyboard
from keyboards.confirmation.yesno import YesNoKeyboard
import re
from uuid import UUID, uuid4
from datetime import datetime
from models.activist import Activist
from models.notification import ActivistDeleteNotif
from notifications.NotificationService import NotificationService


AdminDelMemberRouter = Router()

async def TransitToAdminDelMember(message : Message, storage : BaseStorage, state : FSMContext, logger : Logger):
    await state.set_state(AdminMemberDeletingStates.ChoosingMember)
    validTgUserActivists = storage.GetValidTgUserActivists()
    tmptext = "Выберите пользователя, которого собираетесь удалить"
    await message.answer(tmptext, reply_markup=MemberChoosingKeyboard(validTgUserActivists).Create())

@AdminDelMemberRouter.message(
    AdminMemberDeletingStates.ChoosingMember,
    F.text == MemberChoosingKeyboard.CancelButtonText
)
async def AdminCancelDelMember(message : Message, storage : BaseStorage, state : FSMContext, logger : Logger):
    act = storage.GetAdminByChatID(message.chat.id)
    await TransitToAdminDefault(message=message, state=state, admin=act)

@AdminDelMemberRouter.message(AdminMemberDeletingStates.ChoosingMember)
async def AdminChooseDelMember(message : Message, storage : BaseStorage, state : FSMContext, logger : Logger):
    msg_username = re.search(r'@(\w+)', message.text)
    if msg_username is None:
        await message.answer(f"Пользователя с именем {message.text} нет в списках")
        await TransitToAdminDefault(message=message, state=state, 
                                    admin=storage.GetAdminByChatID(message.chat.id))
        return
    
    act = storage.GetValidTgUserActivistByUsername(msg_username.group(1))
    if act is None:
        await message.answer(f"Пользователя с именем {message.text} нет в списках")
        await TransitToAdminDefault(message=message, state=state, 
                                    admin=storage.GetAdminByChatID(message.chat.id))
        return

    if act.ChatID == message.chat.id:
        await message.answer(f"Вы не можете удалить сами себя")
        await TransitToAdminDefault(message=message, state=state, 
                                    admin=storage.GetAdminByChatID(message.chat.id))
        return

    await state.set_state(AdminMemberDeletingStates.ConfirmingDelMember)
    data = await state.get_data()
    data["id_ActToDel"] = str(act.IDActivist)
    data["name_ActToDel"] = act.Name
    data["username_ActToDel"] = act.Username
    await state.update_data(data)
    await message.answer(f"Вы уверены что хотите удалить пользователя {act.Name} ( @{act.Username} )?", 
                reply_markup=YesNoKeyboard.Create())
    return 

@AdminDelMemberRouter.message(
    AdminMemberDeletingStates.ConfirmingDelMember,
    F.text == YesNoKeyboard.YesButtonText
)
async def AdminCanceledMember(message : Message, storage : BaseStorage, state : FSMContext, logger : Logger, notifServ : NotificationService):
    data = await state.get_data()

    def funcUpdate(act : Activist):
        act.Valid = False
        return act

    activist = storage.GetActivistByID(UUID(data["id_ActToDel"]))

    storage.UpdateValidActivist(UUID(data["id_ActToDel"]), funcUpdate)
    await message.answer(f"Пользователь {data["name_ActToDel"]} ({data["username_ActToDel"]}) был удален")

    # Notification about deleted user
    notif = ActivistDeleteNotif(
        id=uuid4(), 
        text=None,
        notifyTime=datetime.now(),
        ChatIDs=[activist.ChatID],
    )
    await notifServ.AddNotification(notif)

    act = storage.GetAdminByChatID(message.chat.id)
    await TransitToAdminDefault(message=message, state=state, admin=act)

@AdminDelMemberRouter.message(
    AdminMemberDeletingStates.ConfirmingDelMember,
    F.text == YesNoKeyboard.NoButtonText
)
async def AdminCancelAddMember(message : Message, storage : BaseStorage, state : FSMContext, logger : Logger):
    await message.answer(f"Отмена операции")
    act = storage.GetAdminByChatID(message.chat.id)
    await TransitToAdminDefault(message=message, state=state, admin=act)

@AdminDelMemberRouter.message(AdminMemberDeletingStates.ConfirmingDelMember)
async def AdminCancelAddMember(message : Message, storage : BaseStorage, state : FSMContext, logger : Logger):
    await message.answer(f"Ответьте, пожалуйста да/нет")



