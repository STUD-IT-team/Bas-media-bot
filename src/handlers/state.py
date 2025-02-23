from aiogram.fsm.state import StatesGroup, State

class MemberStates(StatesGroup):
    Default = State()
    
class MemberAddingReportStates(StatesGroup):
    Choosing = State()
    ChoosingType = State()
    EnteringLink = State()

class AdminStates(StatesGroup):
    Default = State()

class AdminTaskCreatingStates(StatesGroup):
    EnteringDate = State()
    EnteringPlace = State() 
    EnteringPhoto = State() 
    EnteringVideo = State()
    ChoosingMembers = State()
    ChoosingChief = State()

class AdminTaskCancellingStates(StatesGroup):
    ChoosingReport = State()
    Confirmation = State()

class AdminNewMemberStates(StatesGroup):
    EnteringName = State()
    EnteringTelegramID = State()


class AdminMemberDeletingStates(StatesGroup):
    ChoosingMember = State()

class AdminMailingStates(StatesGroup):
    EnteringText = State()
    EnteringDate = State()
    
