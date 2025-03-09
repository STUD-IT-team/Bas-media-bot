from models import activist
from models import event
from uuid import UUID
class BaseStorage:
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
    
    def GetValidActivists(self) -> list[activist.Activist]:
        raise NotImplementedError
    
    def GetActivistByName(self, name : str) -> activist.Activist:
        raise NotImplementedError

