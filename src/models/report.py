from pydantic import BaseModel, Field
from enum import Enum
from uuid import UUID, uuid4
from models.activist import Activist
from models.event import Event
from typing import Optional
from datetime import datetime

class ReportType(str, Enum):
    Photo = "photo"
    Video = "video"
    

class Report(BaseModel):
    ID : UUID = Field(default_factory=lambda: uuid4())
    EventID: UUID
    Event: Optional[Event] = None
    Type : ReportType
    URL : str
    Activist : Activist
    CreatedAt : datetime = Field(default_factory=lambda: datetime.now())



