from pydantic import BaseModel
from uuid import UUID
from models.event import Event, EventActivist, EventChief
from models.report import Report
from models.activist import Activist
import psycopg2
from psycopg2.extras import RealDictCursor


class ExporterRepository:
    def GetEvent(self, eventId: UUID) -> Event:
        raise NotImplementedError
    
    def GetEventReports(self, eventId: UUID) -> list[Report]:
        raise NotImplementedError


class PostgresCredentials(BaseModel):
    host : str
    port : int
    dbname : str
    user : str
    password : str
    
    def __str__(self):
        return f"host={self.host} port={self.port} dbname={self.dbname} user={self.user} password={self.password}"

class PostgresRepository(ExporterRepository):
    def __init__(self, creds: PostgresCredentials):
        if not isinstance(creds, PostgresCredentials):
            raise ValueError("creds must be an instance of PostgresCredentials")
        
        self._creds = creds
        self._conn = None
    
    def __del__(self):
        if self._conn is not None:
            self._conn.close()
    
    def GetEvent(self, eventId: UUID) -> Event:
        if not isinstance(eventId, UUID):
            raise ValueError("eventId must be an instance of UUID")
        
        if self._conn is None:
            self._conn = psycopg2.connect(str(self._creds))
        
        cur = self._conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT id, evname, evdate, place, photo_amount, video_amount, created_by, created_at
            FROM event
            WHERE id = %s;
        """, (eventId.hex,))
        row = cur.fetchone()
        cur.close()
        eventID = UUID(hex=row['id'])
        chief = self.getEventChief(eventID)
        activists = self.getEventMembers(eventID)
        event = Event(
            ID = eventID,
            Name=row['evname'], 
            Date=row['evdate'], 
            Place=row['place'],
            PhotoCount=row['photo_amount'], 
            VideoCount=row['video_amount'], 
            Chief=chief, 
            Activists=activists,
            CreatedAt=row['created_at'],
            CreatedBy=UUID(hex=row['created_by']),
        )
        return event
    
    def getEventChief(self, eventID) -> EventChief:
        cur = self._conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            SELECT activist.id as acid, event_member.id as eid, chat_id, acname, valid
            FROM activist
            JOIN event_member ON event_member.activist_id = activist.id
            JOIN tg_user ON tg_user.id = activist.tg_user_id
            WHERE event_id = %s AND is_chief = true;
        """, (eventID.hex,))

        row = cur.fetchone()
        cur.close()
        
        if row:
            act = Activist(ID=row['acid'], ChatID=row['chat_id'], Name=row['acname'], Valid=row['valid'])
            return EventChief(ID=row['eid'], EventID=eventID, Activist=act)
        return None
    
    def getEventMembers(self, eventID) -> list[EventActivist]:
        cur = self._conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            SELECT activist.id as acid, event_member.id as eid, chat_id, acname, valid
            FROM activist
            JOIN event_member ON event_member.activist_id = activist.id
            JOIN tg_user ON tg_user.id = activist.tg_user_id
            WHERE event_id = %s AND is_chief = false;
        """, (eventID.hex,))

        rows = cur.fetchall()
        cur.close()
        
        acts = []
        for row in rows:
            act = Activist(ID=row['acid'], ChatID=row['chat_id'], Name=row['acname'], Valid=row['valid'])
            acts.append(EventActivist(ID=row['eid'], EventID=eventID, Activist=act))
        return acts
    
    def GetEventReports(self, eventId: UUID) -> list[Report]:
        if not isinstance(eventId, UUID):
            raise ValueError("eventId must be an instance of UUID")
        
        if self._conn is None:
            self._conn = psycopg2.connect(str(self._creds))
        
        cur = self._conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT report.id as report_id, report.event_member_id, report.report_type, report.url, report.created_at, activist.id as activist_id
            FROM report JOIN event_member ON event_member.id = report.event_member_id
            JOIN activist ON activist.id = event_member.activist_id
            WHERE event_member.event_id = %s;
        """, (eventId.hex,))
        rows = cur.fetchall()
        cur.close()
        reports = []
        for row in rows:
            reportID = UUID(hex=row['report_id'])
            eventMemberID = UUID(hex=row['event_member_id'])
            reportType = row['report_type']
            url = row['url']
            createdAt = row['created_at']
            activistID = UUID(hex=row['activist_id'])
            activist = self.GetActivistByID(activistID)
            reports.append(Report(ID=reportID, EventMemberID=eventMemberID, Type=reportType, URL=url, CreatedAt=createdAt, Activist=activist, EventID=eventId))
        return reports
    
    def GetActivistByID(self, ID: UUID) -> Activist:
        if not isinstance(ID, UUID):
            raise ValueError("ID must be an instance of UUID")
        
        if self._conn is None:
            self._conn = psycopg2.connect(str(self._creds))
        
        cur = self._conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT activist.id, chat_id, acname, valid
            FROM activist JOIN tg_user
            ON tg_user.id = activist.tg_user_id
            WHERE activist.id = %s;
        """, (ID.hex,))
        row = cur.fetchone()
        cur.close()
        if row:
            act = Activist(ID=row['id'], ChatID=row['chat_id'], Name=row['acname'], Valid=row['valid'])
            return act
        return None
