from pydantic import BaseModel

class TelegramUserAgreement(BaseModel):
    ChatID : int
    Username : str
    Agreed : bool
