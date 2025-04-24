from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from models.activist import Activist

class EventChief(BaseModel):
    ID : UUID
    EventID : UUID
    Activist : Activist

class EventActivist(BaseModel):
    ID : UUID
    EventID : UUID
    Activist : Activist

class Event(BaseModel):
    ID : UUID
    Name : str
    Date : datetime
    Place : str
    PhotoCount : int
    VideoCount : int
    Chief : EventChief
    Activists : list[EventActivist]
    IsCancelled : bool = False
    IsCompleted : bool = False
    CreatedBy : UUID
    CreatedAt : datetime

class CanceledEvent(Event):
    IsCancelled : bool = True
    CanceledAt : datetime
    CanceledBY : UUID

class CompletedEvent(Event):
    IsCompleted : bool = True
    CompletedAt : datetime
    CompletedBy : UUID

class EventForActivist(BaseModel):
    ID: UUID
    Name: str
    Date : datetime
    Chief: Activist
    ChiefTgNick: str
    PhotoCount : int
    VideoCount : int