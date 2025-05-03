from handlers.state import AdminAddNotificationStates
from handlers.usertransition import TransitToAdminDefault
from aiogram import F
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import or_f
from storage.storage import BaseStorage
from logging import Logger
from keyboards.confirmation.cancel import CancelKeyboard
from keyboards.confirmation.yesno import YesNoKeyboard
from keyboards.activist.choosing import MemberChoosingCancelKeyboard
from datetime import datetime
from uuid import UUID, uuid4
from utils.strings import NewlineJoin, EnumerateStrings
from models.activist import Activist
from notifications.NotificationService import NotificationService
from models.notification import MapperNotification

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
KEY_NOTIF_CHATIDS = 'NotificationActivistsID'
KEY_NOTIF_TIME = "NotificationTime"
KEY_NOTIF_TEXT = "NotificationText"

AdminAddNotificationRouter = Router()

async def TransitToAdminAddNotification(message : Message, storage : BaseStorage, state : FSMContext, logger : Logger):
    logger.info(f"Transit To Admin Add Notification")
    await state.set_state(AdminAddNotificationStates.EnteringText)
    logger.info(f"STATE = AdminAddNotificationStates.EnteringText")
    tmptext = "Введите текст уведомления: "
    await message.answer(tmptext, reply_markup=CancelKeyboard.Create())

@AdminAddNotificationRouter.message(
    or_f(
        AdminAddNotificationStates.EnteringText,
        AdminAddNotificationStates.EnteringTime,
        AdminAddNotificationStates.EnteringUsers
    ),
    F.text == CancelKeyboard.CancelButtonText
)
async def AdminCancelAddNotification(message : Message, storage : BaseStorage, state : FSMContext, logger : Logger):
    logger.info(f"Admin Cancel Add Notification")
    admin = storage.GetAdminByChatID(message.chat.id)
    await message.answer(f"Уведомление не создано.")
    await TransitToAdminDefault(message=message, state=state, admin=admin)

@AdminAddNotificationRouter.message(AdminAddNotificationStates.EnteringText)
async def AdminEnteringText(message : Message, storage : BaseStorage, state : FSMContext, logger : Logger):
    logger.info(f"Admin Entering Text")
    data = await state.get_data()
    data[KEY_NOTIF_TEXT] = message.text
    await state.update_data(data)
    await state.set_state(AdminAddNotificationStates.EnteringTime)
    logger.info(f"STATE = AdminAddNotificationStates.EnteringTime")
    await message.answer("Введите время, когда уведомление будет отправлено, в формате: " + \
                         "сейчас/ГГГГ-ММ-ДД ЧЧ:ММ:СС", 
                         reply_markup=CancelKeyboard.Create())
    
def GetNotChosenChatIDs(storage : BaseStorage, context : dict[str, any]) -> list[Activist]:
    acts = storage.GetValidActivists()
    chosenChatIDs = [int(chatID) for chatID in context[KEY_NOTIF_CHATIDS]]
    acts = list(filter(lambda a: a.ChatID not in chosenChatIDs, acts))
    return acts

@AdminAddNotificationRouter.message(AdminAddNotificationStates.EnteringTime)
async def AdminEnteringTime(message : Message, storage : BaseStorage, state : FSMContext, logger : Logger):
    logger.info(f"Admin Entering Time")
    timeText = message.text
    if timeText.lower().strip() == "сейчас":
        timeRes = datetime.now()
    else:  
         # Преобразование в datetime
        try:
            timeText = timeText.strip()
            date_str, time_str = timeText.split()
            timeRes = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
        except Exception as e:
            await message.answer("Время введено в неверном формате.")
            await message.answer("Введите время, когда уведомление будет отправлено, в формате: " + \
                                "сейчас/ГГГГ-ММ-ДД ЧЧ:ММ:СС", 
                                reply_markup=CancelKeyboard.Create())
            return
        if timeRes < datetime.now():
            await message.answer("Введите время в будущем.")
            await message.answer("Введите время, когда уведомление будет отправлено, в формате: " + \
                                "сейчас/ГГГГ-ММ-ДД ЧЧ:ММ:СС", 
                                reply_markup=CancelKeyboard.Create())
            return
        
    # # Преобразуем строку обратно в datetime
    # saved_datetime = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    data = await state.get_data()
    data[KEY_NOTIF_TIME] = timeRes.strftime(TIME_FORMAT)
    data[KEY_NOTIF_CHATIDS] = []
    await state.update_data(data)
    await state.set_state(AdminAddNotificationStates.EnteringUsers)
    logger.info(f"STATE = AdminAddNotificationStates.EnteringUsers")
    await message.answer("Введите пользователей, которым хотите отправить уведомление: ", 
        reply_markup=MemberChoosingCancelKeyboard(GetNotChosenChatIDs(storage, data)).Create())
    
@AdminAddNotificationRouter.message(
    AdminAddNotificationStates.EnteringUsers,
    F.text == MemberChoosingCancelKeyboard.StopActivistChoosingButtonText
)
async def AdminEnteringUsersStop(message: Message, storage: BaseStorage, state: FSMContext, logger: Logger):
    logger.info(f"Admin Entering Users Stop")
    data = await state.get_data()
    textNotif = data[KEY_NOTIF_TEXT]
    try:
        timeNotif = datetime.strptime(data[KEY_NOTIF_TIME], TIME_FORMAT)
    except ValueError:
        raise Exception("В dateContext записано время в неверном формате, такого быть не должно!")
    chatIDsNotif = data[KEY_NOTIF_CHATIDS]

    if len(chatIDsNotif) == 0:
        await message.answer(f"Вы не добавили ни одного получателя уведомления. \nДобавьте хотябы одного.")
        await message.answer("Введите пользователей, которым хотите отправить уведомление: ", 
            reply_markup=MemberChoosingCancelKeyboard(GetNotChosenChatIDs(storage, data)).Create())
        return

    notifActivists = [storage.GetActivistByChatID(chat_id) for chat_id in chatIDsNotif]
    await message.answer(NewlineJoin(
        f"<b>Текст уведомления:</b> \n{textNotif}",
        f"<b>Время отправления:</b> {timeNotif}",
        f"<b>Кому будет отправлено:</b>",
        *EnumerateStrings(*[act.Name for act in notifActivists]),
        ""
        "Данные верны?"
    ), reply_markup=YesNoKeyboard.Create())
    await state.set_state(AdminAddNotificationStates.Confirmation)
    logger.info(f"STATE = AdminAddNotificationStates.Confirmation")

@AdminAddNotificationRouter.message(
    AdminAddNotificationStates.EnteringUsers
)
async def AdminEnteringUsers(message: Message, storage: BaseStorage, state: FSMContext, logger: Logger):
    logger.info(f"Admin Entering Users")
    data = await state.get_data()
    activistName = message.text
    act = storage.GetActivistByName(activistName)
    if act is None:
        await message.answer(f"Активист с именем {activistName} не найден.")
        await message.answer("Введите пользователей, которым хотите отправить уведомление: ", 
            reply_markup=MemberChoosingCancelKeyboard(GetNotChosenChatIDs(storage, data)).Create())
    
    data[KEY_NOTIF_CHATIDS].append(str(act.ChatID))
    await state.update_data(data)
    await message.answer(f"Активист с именем {activistName} добавлен.")
    await message.answer("Введите пользователей, которым хотите отправить уведомление: ", 
            reply_markup=MemberChoosingCancelKeyboard(GetNotChosenChatIDs(storage, data)).Create())
    


@AdminAddNotificationRouter.message(
    AdminAddNotificationStates.Confirmation,
    F.text == YesNoKeyboard.YesButtonText
)
async def AdminConfirmedNotification(message: Message, storage: BaseStorage, state: FSMContext, logger: Logger, notifServ: NotificationService):
    logger.info(f"Admin Confirmed Notification")
    data = await state.get_data()
    textNotif = data[KEY_NOTIF_TEXT]
    try:
        timeNotif = datetime.strptime(data[KEY_NOTIF_TIME], TIME_FORMAT)
    except ValueError:
        raise Exception("В dateContext записано время в неверном формате, такого быть не должно!")
    chatIDsNotif = data[KEY_NOTIF_CHATIDS]

    try:
        notif = MapperNotification.CreateNotification(
            'info', 
            uuid4(),
            textNotif,
            timeNotif, 
            chatIDsNotif)
        await notifServ.AddNotification(notif)
    except BaseException as e:
        logger.error(f"Error occurred while creating and adding notification: {str(e)}")
        await message.answer(f"Произошла ошибка при создании уведомления.")
    
    admin = storage.GetAdminByChatID(message.chat.id)
    await TransitToAdminDefault(message=message, state=state, admin=admin)

@AdminAddNotificationRouter.message(
    AdminAddNotificationStates.Confirmation,
    F.text == YesNoKeyboard.NoButtonText
)
async def AdminCanceledNotifCreation(message: Message, storage: BaseStorage, state: FSMContext, logger: Logger):
    admin = storage.GetAdminByChatID(message.chat.id)
    await message.answer(f"Уведомление не создано.")
    await TransitToAdminDefault(message=message, state=state, admin=admin)
