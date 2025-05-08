from pydantic import BaseModel
from uuid import UUID


class Activist(BaseModel):
    ID : UUID
    ChatID : int
    Name : str
    Valid : bool


class Admin(BaseModel):
    ID : UUID
    UserName : str
    Name : str
    ChatID : int
    Valid : bool


class TgUser(BaseModel):
    ID : UUID
    ChatID : int
    Username : str
    Agreed : bool


class TgUserActivist(BaseModel):
    IDTgUser : UUID
    IDActivist : UUID
    ChatID : int
    Username : str
    Name : str
    Valid : bool
    Agreed : bool
