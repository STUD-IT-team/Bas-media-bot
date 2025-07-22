from pydantic import BaseModel
from uuid import UUID
from models.event import Event, EventActivist, EventChief
from models.report import Report
from models.activist import Activist
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager


class ExporterRepository:
    def GetEvent(self, eventId: UUID) -> Event:
        raise NotImplementedError
    
    def GetEventReports(self, eventId: UUID) -> list[Report]:
        raise NotImplementedError


class PostgresCredentials(BaseModel):
    host: str
    port: int
    dbname: str
    user: str
    password: str
    
    def __str__(self):
        return f"host={self.host} port={self.port} dbname={self.dbname} user={self.user} password={self.password}"


class PostgresRepository(ExporterRepository):
    def __init__(self, creds: PostgresCredentials):
        if not isinstance(creds, PostgresCredentials):
            raise ValueError("creds must be an instance of PostgresCredentials")
        
        self._creds = creds
        self._pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=10,
            **creds.model_dump()
        )
    
    def __del__(self):
        if hasattr(self, '_pool'):
            self._pool.closeall()
    
    @contextmanager
    def _get_dict_cursor(self):
        conn = self._pool.getconn()
        try:
            yield conn.cursor(cursor_factory=RealDictCursor)
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self._pool.putconn(conn)

    def GetEvent(self, eventId: UUID) -> Event:
        if not isinstance(eventId, UUID):
            raise ValueError("eventId must be an instance of UUID")
        
        with self._get_dict_cursor() as cur:
            cur.execute("""
                SELECT id, evname, evdate, place, photo_amount, video_amount, created_by, created_at
                FROM event
                WHERE id = %s;
            """, (eventId.hex,))
            row = cur.fetchone()
            if not row:
                raise ValueError(f"Event with ID {eventId} not found")
            
            eventID = UUID(hex=row['id'])
            chief = self.getEventChief(eventID)
            activists = self.getEventMembers(eventID)
            return Event(
                ID=eventID,
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
    
    def getEventChief(self, eventID) -> EventChief:
        with self._get_dict_cursor() as cur:
            cur.execute("""
                SELECT activist.id as acid, event_member.id as eid, chat_id, acname, valid
                FROM activist
                JOIN event_member ON event_member.activist_id = activist.id
                JOIN tg_user ON tg_user.id = activist.tg_user_id
                WHERE event_id = %s AND is_chief = true;
            """, (eventID.hex,))
            row = cur.fetchone()
            if row:
                act = Activist(ID=row['acid'], ChatID=row['chat_id'], Name=row['acname'], Valid=row['valid'])
                return EventChief(ID=row['eid'], EventID=eventID, Activist=act)
        return None
    
    def getEventMembers(self, eventID) -> list[EventActivist]:
        with self._get_dict_cursor() as cur:
            cur.execute("""
                SELECT activist.id as acid, event_member.id as eid, chat_id, acname, valid
                FROM activist
                JOIN event_member ON event_member.activist_id = activist.id
                JOIN tg_user ON tg_user.id = activist.tg_user_id
                WHERE event_id = %s AND is_chief = false;
            """, (eventID.hex,))
            
            return [
                EventActivist(
                    ID=row['eid'], 
                    EventID=eventID, 
                    Activist=Activist(
                        ID=row['acid'], 
                        ChatID=row['chat_id'], 
                        Name=row['acname'], 
                        Valid=row['valid']
                    )
                ) for row in cur.fetchall()
            ]
    
    def GetEventReports(self, eventId: UUID) -> list[Report]:
        if not isinstance(eventId, UUID):
            raise ValueError("eventId must be an instance of UUID")
        
        with self._get_dict_cursor() as cur:
            cur.execute("""
                SELECT report.id as report_id, report.event_member_id, report.report_type, report.url, 
                       report.created_at, activist.id as activist_id
                FROM report 
                JOIN event_member ON event_member.id = report.event_member_id
                JOIN activist ON activist.id = event_member.activist_id
                WHERE event_member.event_id = %s;
            """, (eventId.hex,))
            
            reports = []
            for row in cur.fetchall():
                activist = self.GetActivistByID(UUID(hex=row['activist_id']))
                reports.append(Report(
                    ID=UUID(hex=row['report_id']),
                    EventMemberID=UUID(hex=row['event_member_id']),
                    Type=row['report_type'],
                    URL=row['url'],
                    CreatedAt=row['created_at'],
                    Activist=activist,
                    EventID=eventId
                ))
            return reports
    
    def GetActivistByID(self, ID: UUID) -> Activist:
        if not isinstance(ID, UUID):
            raise ValueError("ID must be an instance of UUID")
        
        with self._get_dict_cursor() as cur:
            cur.execute("""
                SELECT activist.id, chat_id, acname, valid
                FROM activist JOIN tg_user
                ON tg_user.id = activist.tg_user_id
                WHERE activist.id = %s;
            """, (ID.hex,))
            row = cur.fetchone()
            if row:
                return Activist(
                    ID=row['id'],
                    ChatID=row['chat_id'],
                    Name=row['acname'],
                    Valid=row['valid']
                )
        return None