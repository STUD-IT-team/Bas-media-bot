from models import activist
from models import event
from models import telegram
from uuid import UUID
class BaseStorage:
    def GetTelegramUserPersonalDataAgreement(self, chatID) -> telegram.TelegramUserAgreement:
        raise NotImplementedError
    def SetTelegramUserPersonalDataAgreement(self, agreement: telegram.TelegramUserAgreement):
        raise NotImplementedError
    def GetActivistByChatID(self, chatID : int) -> activist.Activist:
        raise NotImplementedError
    def GetActivistByID(self, ID : UUID):
        raise NotImplementedError
    
    def GetAdminByChatID(self, chatID : int) -> activist.Admin:
        raise NotImplementedError
    
    def PutTgUser(self, chat_id : int, username : str):
        raise NotImplementedError
    
    def PutEvent(self, event: event.Event):
        raise NotImplementedError
    
    def CancelEvent(self, event_id: UUID, canceled_by: UUID):
        raise NotImplementedError    
    
    def GetValidActivists(self) -> list[activist.Activist]:
        raise NotImplementedError
    
    def GetActivistByName(self, name : str) -> activist.Activist:
        raise NotImplementedError
    
    def GetActiveEvents(self) -> list[event.Event] :
        raise NotImplementedError
        

