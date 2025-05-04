from aiogram.fsm.state import StatesGroup, State

class MemberStates(StatesGroup):
    Default = State()
    
class MemberReportAddingStates(StatesGroup):
    Choosing = State()
    ChoosingType = State()
    EnteringLink = State()

class AdminStates(StatesGroup):
    Default = State()
    AdminCancellingEvent=State()
    AdminCompletingEvent=State()

class AdminEventCreatingStates(StatesGroup):
    EnteringName = State()
    EnteringDate = State()
    EnteringPlace = State() 
    EnteringPhotoCount = State() 
    EnteringVideoCount = State()
    ChoosingMembers = State()
    ChoosingChief = State()
    Confirmation = State()

class AdminTaskCancellingStates(StatesGroup):
    ChoosingReport = State()
    Confirmation = State()

class AdminNewMemberStates(StatesGroup):
    EnteringName = State()
    EnteringTelegramID = State()


class AdminMemberDeletingStates(StatesGroup):
    ChoosingMember = State()
    ConfirmingDelMember = State()

class AdminMailingStates(StatesGroup):
    EnteringText = State()
    EnteringDate = State()
    
