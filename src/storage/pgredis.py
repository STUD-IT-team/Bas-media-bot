from pydantic import BaseModel
from pydantic_core import from_json
from storage.storage import BaseStorage
from models.activist import Activist, Admin
from models.event import Event, EventActivist, EventChief
from models.telegram import TelegramUserAgreement
from uuid import UUID
from psycopg2.extras import RealDictCursor
import psycopg2

import redis

class PostgresCredentials(BaseModel):
    host : str
    port : int
    dbname : str
    user : str
    password : str
    
    def __str__(self):
        return f"host={self.host} port={self.port} dbname={self.dbname} user={self.user} password={self.password}"


class RedisCredentials(BaseModel):
    host : str
    port : int
    user : str
    password : str
    db : int

class PgRedisStorage(BaseStorage):
    def __init__(self, pgcred: PostgresCredentials, redCred: RedisCredentials):
        self.conn = psycopg2.connect(str(pgcred))

        self.redis = redis.Redis(
            host=redCred.host,
            port=redCred.port,
            username=redCred.user,
            password=redCred.password,
            db=redCred.db,
            decode_responses=True
        )

        if not self.redis.ping():
            raise Exception("Failed to connect to Redis")
    
    def __del__(self):
        self.conn.close()
        self.redis.close()
    
    def GetTelegramUserPersonalDataAgreement(self, chatID) -> TelegramUserAgreement:
        agreement = self.redis.get(name=str(chatID))
        if agreement is not None:
            return TelegramUserAgreement.model_validate_json(agreement)
        cur = self.conn.cursor()
        cur.execute("""
            SELECT chat_id, tg_username, agreed FROM tg_user WHERE chat_id = %s;
        """, (chatID,))
        row = cur.fetchone()
        cur.close()
        if row:
            agreement = TelegramUserAgreement(ChatID=row[0], Username=row[1], Agreed=row[2])
            try:
                self.redis.delete(str(chatID))
                self.redis.set(name=str(chatID), value=agreement.model_dump_json())
            finally:
                return agreement
        return None
    
    def SetTelegramUserPersonalDataAgreement(self, agreement: TelegramUserAgreement):
        cur = self.conn.cursor()
        self.PutTgUser(agreement.ChatID, agreement.Username)
        cur.execute("""
            UPDATE tg_user SET agreed = %s WHERE chat_id = %s;
        """, (agreement.Agreed, agreement.ChatID))

        self.conn.commit()
        cur.close()

        try:
            self.redis.delete(str(chatID))
            self.redis.set(name=str(chatID), value=agreement.model_dump_json())
        finally:
            return


    def PutTgUser(self, chat_id : int, username : str):
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO tg_user (id, chat_id, tg_username) VALUES (gen_random_uuid (), %s, %s) ON CONFLICT (chat_id) DO UPDATE SET tg_username = EXCLUDED.tg_username;
        """, (chat_id, username))
        self.conn.commit()

    def GetActivistByChatID(self, chatID : int) -> Activist:

        cur = self.conn.cursor()

        cur.execute("""
            SELECT activist.id, chat_id, acname, valid FROM activist JOIN tg_user ON tg_user.id = activist.tg_user_id WHERE chat_id = %s AND valid = true;
        """, (chatID,))

        row = cur.fetchone()
        cur.close()
        
        act = None
        if row:
            act = Activist(ID=row[0], ChatID=row[1], Name=row[2], Valid=row[3])
        return act
    
    def GetActivistByID(self, ID : UUID):
        cur = self.conn.cursor()
        cur.execute("""
            SELECT activist.id, chat_id, acname, valid FROM activist JOIN tg_user ON tg_user.id = activist.tg_user_id WHERE activist.id = %s AND valid = true;
        """, (ID.hex,))
        row = cur.fetchone()
        cur.close()
        act = None
        if row:
            act = Activist(ID=row[0], ChatID=row[1], Name=row[2], Valid=row[3])
        return act
    
    def GetAdminByChatID(self, chatID : int) -> Admin:
        cur = self.conn.cursor()

        cur.execute("""
            SELECT tg_admin.id, tg_user.chat_id, tg_user.tg_username, tg_admin.adname, tg_admin.valid FROM tg_admin JOIN tg_user ON tg_user.id = tg_admin.tg_user_id WHERE chat_id = %s;
        """, (chatID,))

        row = cur.fetchone()
        cur.close()
        
        adm = None
        if row:
            adm = Admin(ID=row[0], ChatID=row[1], UserName=row[2], Name=row[3], Valid=row[4])
        return adm
    
    def PutEvent(self, event: Event):
        cur = self.conn.cursor()
        try:
            cur.execute("""
                INSERT INTO event (id, evname, evdate, place, photo_amount, video_amount, created_by, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;
            """, (event.ID.hex, event.Name, event.Date, event.Place, event.PhotoCount, event.VideoCount, event.CreatedBy.hex, event.CreatedAt))

            if event.IsCancelled and isinstance(event, CancelledEvent):
                cur.execute("""
                    INSERT INTO canceled_event (event_id, canceled_by, canceled_at) VALUES (%s, %s, %s)
                """, (event.ID.hex, event.CancelledBy.hex, event.CanceledAt))
            elif event.IsCompleted and isinstance(event, CompletedEvent):
                cur.execute("""
                    INSERT INTO completed_event (event_id, completed_by, completed_at) VALUES (%s, %s, %s)
                """, (event.ID.hex, event.CompletedBy.hex, event.CompletedAt))

            # Inserting activists
            cur.execute("""
                INSERT INTO event_member (id, event_id, activist_id, is_chief) VALUES (gen_random_uuid(), %s, %s, true)
            """, (event.ID.hex, event.Chief.Activist.ID.hex))
            for act in event.Activists:
                cur.execute("""
                    INSERT INTO event_member (id, event_id, activist_id, is_chief) VALUES (gen_random_uuid(), %s, %s, false)
                """, (event.ID.hex, act.Activist.ID.hex))
            
            self.conn.commit()
        except psycopg2.Error:
            self.conn.rollback()
            raise
        cur.close()

    def GetValidActivists(self) -> list[Activist]:
        cur = self.conn.cursor()

        cur.execute("""
            SELECT activist.id, chat_id, acname, valid FROM activist JOIN tg_user ON tg_user.id = activist.tg_user_id WHERE valid = true;
        """)

        rows = cur.fetchall()
        cur.close()
        
        acts = []
        for row in rows:
            acts.append(Activist(ID=row[0], ChatID=row[1], Name=row[2], Valid=row[3]))
        return acts

    def GetActivistByName(self, name : str) -> Activist:
        cur = self.conn.cursor()
        cur.execute("""
            SELECT activist.id, chat_id, acname, valid FROM activist JOIN tg_user ON tg_user.id = activist.tg_user_id WHERE acname = %s AND valid = true;
        """, (name,))
        row = cur.fetchone()
        cur.close()

        if row:
            act = Activist(ID=row[0], ChatID=row[1], Name=row[2], Valid=row[3])
            return act
        return None

    
    def GetActiveEvents(self) -> list[Event]:
        cur = self.conn.cursor(cursor_factory=RealDictCursor)

        # Ура, хоть раз в жизни anti-join пригодился @Impervguin
        cur.execute("""
            SELECT id, evname, evdate, place, photo_amount, video_amount, created_by, created_at
            FROM event
            WHERE NOT EXISTS (
                SELECT *
                FROM completed_event
                WHERE event_id = event.id
            ) AND NOT EXISTS (
                SELECT *
                FROM canceled_event
                WHERE event_id = event.id
            )
        """)

        rows = cur.fetchall()
        cur.close()
        events = []
        for row in rows:
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
            events.append(event)
        return events
    def getEventChief(self, eventID) -> EventChief:
        cur = self.conn.cursor(cursor_factory=RealDictCursor)

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
        cur = self.conn.cursor(cursor_factory=RealDictCursor)

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



