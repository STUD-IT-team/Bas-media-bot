from pydantic import BaseModel
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
    ID : UUID = uuid4()
    EventID: UUID
    Event: Optional[Event] = None
    Type : ReportType
    URL : str
    Activist : Activist
    CreatedAt : datetime = datetime.now()


