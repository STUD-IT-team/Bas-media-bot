from storage import domain
class BaseStorage:
    def GetActivistByChatID(self, chatID : int) -> domain.Activist:
        raise NotImplementedError
    
    def GetAdminByChatID(self, chatID : int) -> domain.Admin:
        raise NotImplementedError
    
    def PutTgUser(self, chat_id : int, username : str):
        raise NotImplementedError