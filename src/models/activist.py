from pydantic import BaseModel
from uuid import UUID

class Activist(BaseModel):
    ID : UUID
    ChatID : int
    Name : str
    Valid : bool

class Admin(BaseModel):
    ID : UUID
    ChatID : int

class TgUser(BaseModel):
    ID : UUID
    ChatID : int
    Username : str
    Agreed : bool