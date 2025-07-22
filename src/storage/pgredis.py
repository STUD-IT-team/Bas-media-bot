from pydantic import BaseModel
from pydantic_core import from_json
from storage.storage import BaseStorage
from models.activist import Activist, Admin, TgUser, TgUserActivist
from models.event import Event, EventActivist, EventChief, EventForActivist
from models.notification import BaseNotification, BaseNotifWithEvent, NotifRegistryBase
from models.telegram import TelegramUserAgreement
from models.event import CanceledEvent, CompletedEvent
from models.report import Report
from uuid import UUID
from datetime import datetime
from psycopg2.extras import RealDictCursor
import psycopg2
from psycopg2 import pool
import redis
from contextlib import contextmanager

class PostgresCredentials(BaseModel):
    host: str
    port: int
    dbname: str
    user: str
    password: str
    
    def __str__(self):
        return f"host={self.host} port={self.port} dbname={self.dbname} user={self.user} password={self.password}"

class RedisCredentials(BaseModel):
    host: str
    port: int
    user: str
    password: str
    db: int

class PgRedisStorage(BaseStorage):
    def __init__(self, pgcred: PostgresCredentials, redCred: RedisCredentials):
        self.pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=10,
            **pgcred.model_dump()
        )
        
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
        if hasattr(self, 'pool'):
            self.pool.closeall()
        if hasattr(self, 'redis'):
            self.redis.close()
    
    @contextmanager
    def _get_cursor(self):
        conn = self.pool.getconn()
        try:
            yield conn.cursor()
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.pool.putconn(conn)
    
    @contextmanager
    def _get_dict_cursor(self):
        conn = self.pool.getconn()
        try:
            yield conn.cursor(cursor_factory=RealDictCursor)
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.pool.putconn(conn)

    def GetTelegramUserPersonalDataAgreement(self, chatID) -> TelegramUserAgreement:
        agreement = self.redis.get(name=str(chatID))
        if agreement is not None:
            return TelegramUserAgreement.model_validate_json(agreement)
        
        with self._get_cursor() as cur:
            cur.execute("""
                SELECT chat_id, tg_username, agreed FROM tg_user WHERE chat_id = %s;
            """, (chatID,))
            row = cur.fetchone()
            if row:
                agreement = TelegramUserAgreement(ChatID=row[0], Username=row[1], Agreed=row[2])
                try:
                    self.redis.delete(str(chatID))
                    self.redis.set(name=str(chatID), value=agreement.model_dump_json())
                finally:
                    return agreement
        return None
    
    def SetTelegramUserPersonalDataAgreement(self, agreement: TelegramUserAgreement):
        with self._get_cursor() as cur:
            self.PutTgUser(agreement.ChatID, agreement.Username)
            cur.execute("""
                UPDATE tg_user SET agreed = %s WHERE chat_id = %s;
            """, (agreement.Agreed, agreement.ChatID))
            
            try:
                self.redis.delete(str(agreement.ChatID))
                self.redis.set(name=str(agreement.ChatID), value=agreement.model_dump_json())
            except:
                pass

    def PutTgUser(self, chat_id: int, username: str):
        with self._get_cursor() as cur:
            cur.execute("""
                INSERT INTO tg_user (id, chat_id, tg_username) 
                VALUES (gen_random_uuid(), %s, %s) 
                ON CONFLICT (chat_id) DO UPDATE SET tg_username = EXCLUDED.tg_username;
            """, (chat_id, username))

    def GetActivistByChatID(self, chatID: int) -> Activist:
        with self._get_cursor() as cur:
            cur.execute("""
                SELECT activist.id, chat_id, acname, valid 
                FROM activist JOIN tg_user ON tg_user.id = activist.tg_user_id 
                WHERE chat_id = %s AND valid = true;
            """, (chatID,))
            row = cur.fetchone()
            if row:
                return Activist(ID=row[0], ChatID=row[1], Name=row[2], Valid=row[3])
        return None
    
    def GetActivistByID(self, ID: UUID) -> Activist:
        with self._get_cursor() as cur:
            cur.execute("""
                SELECT activist.id, chat_id, acname, valid 
                FROM activist JOIN tg_user 
                ON tg_user.id = activist.tg_user_id 
                WHERE activist.id = %s AND valid = true;
            """, (ID.hex,))
            row = cur.fetchone()
            if row:
                return Activist(ID=row[0], ChatID=row[1], Name=row[2], Valid=row[3])
        return None
    
    def GetAdminByChatID(self, chatID: int) -> Admin:
        with self._get_cursor() as cur:
            cur.execute("""
                SELECT tg_admin.id, tg_user.chat_id, tg_user.tg_username, tg_admin.adname, tg_admin.valid 
                FROM tg_admin JOIN tg_user ON tg_user.id = tg_admin.tg_user_id 
                WHERE chat_id = %s;
            """, (chatID,))
            row = cur.fetchone()
            if row:
                return Admin(ID=row[0], ChatID=row[1], UserName=row[2], Name=row[3], Valid=row[4])
        return None
    
    def PutEvent(self, event: Event):
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO event (id, evname, evdate, place, photo_amount, video_amount, created_by, created_at) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;
                """, (event.ID.hex, event.Name, event.Date, event.Place, event.PhotoCount, event.VideoCount, event.CreatedBy.hex, event.CreatedAt))

                if event.IsCancelled and isinstance(event, CancelledEvent):
                    cur.execute("""
                        INSERT INTO canceled_event (event_id, canceled_by, canceled_at) 
                        VALUES (%s, %s, %s)
                    """, (event.ID.hex, event.CancelledBY.hex, event.CanceledAt))
                elif event.IsCompleted and isinstance(event, CompletedEvent):
                    cur.execute("""
                        INSERT INTO completed_event (event_id, completed_by, completed_at) 
                        VALUES (%s, %s, %s)
                    """, (event.ID.hex, event.CompletedBy.hex, event.CompletedAt))

                cur.execute("""
                    INSERT INTO event_member (id, event_id, activist_id, is_chief) 
                    VALUES (gen_random_uuid(), %s, %s, true)
                """, (event.ID.hex, event.Chief.Activist.ID.hex))
                
                for act in event.Activists:
                    cur.execute("""
                        INSERT INTO event_member (id, event_id, activist_id, is_chief) 
                        VALUES (gen_random_uuid(), %s, %s, false)
                    """, (event.ID.hex, act.Activist.ID.hex))
                
                conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.pool.putconn(conn)

    def GetValidActivists(self) -> list[Activist]:
        with self._get_cursor() as cur:
            cur.execute("""
                SELECT activist.id, chat_id, acname, valid 
                FROM activist JOIN tg_user 
                ON tg_user.id = activist.tg_user_id 
                WHERE valid = true;
            """)
            return [Activist(ID=row[0], ChatID=row[1], Name=row[2], Valid=row[3]) for row in cur.fetchall()]

    def GetValidTgUserActivists(self) -> list[TgUserActivist]:
        with self._get_cursor() as cur:
            cur.execute("""
                SELECT tu.id, ac.id, tu.chat_id, tu.tg_username, ac.acname, ac.valid, tu.agreed
                FROM tg_user tu
                JOIN activist ac
                ON tu.id = ac.tg_user_id
                WHERE ac.valid = true;
            """)
            return [
                TgUserActivist(
                    IDTgUser=row[0], IDActivist=row[1], 
                    ChatID=row[2], Username=row[3],
                    Name=row[4], Valid=row[5], Agreed=row[6]
                ) for row in cur.fetchall()
            ]

    def GetValidTgUserActivistByUsername(self, username: str) -> TgUserActivist:
        with self._get_cursor() as cur:
            cur.execute("""
                SELECT tu.id, ac.id, tu.chat_id, tu.tg_username, ac.acname, ac.valid, tu.agreed
                FROM tg_user tu
                JOIN activist ac
                ON tu.id = ac.tg_user_id
                WHERE tu.tg_username = %s
                AND ac.valid = true
            """, (username,))
            row = cur.fetchone()
            if row:
                return TgUserActivist(
                    IDTgUser=row[0], IDActivist=row[1], 
                    ChatID=row[2], Username=row[3],
                    Name=row[4], Valid=row[5], Agreed=row[6]
                )
        return None

    def GetActivistByName(self, name: str) -> Activist:
        with self._get_cursor() as cur:
            cur.execute("""
                SELECT activist.id, chat_id, acname, valid 
                FROM activist JOIN tg_user 
                ON tg_user.id = activist.tg_user_id 
                WHERE acname = %s AND valid = true;
            """, (name,))
            row = cur.fetchone()
            if row:
                return Activist(ID=row[0], ChatID=row[1], Name=row[2], Valid=row[3])
        return None
    
    def CancelEvent(self, event_id: UUID, cancelled_by: UUID):
        with self._get_cursor() as cur:
            cur.execute("""
                INSERT INTO canceled_event (event_id, canceled_by, canceled_at)
                VALUES (%s, %s, %s)
            """, (event_id.hex, cancelled_by.hex, datetime.now()))
    
    def CompleteEvent(self, event_id: UUID, completed_by: UUID):
        with self._get_cursor() as cur:
            cur.execute("""
                INSERT INTO completed_event (event_id, completed_by, completed_at)
                VALUES (%s, %s, %s)
            """, (event_id.hex, completed_by.hex, datetime.now()))

    def GetEvents(self) -> list[Event]:
        events = []
        with self._get_dict_cursor() as cur:
            cur.execute("""
                SELECT id, evname, evdate, place, photo_amount, video_amount, created_by, created_at
                FROM event
            """)
            for row in cur.fetchall():
                eventID = UUID(hex=row['id'])
                chief = self.getEventChief(eventID)
                activists = self.getEventMembers(eventID)
                events.append(Event(
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
                ))
        return events

    def GetActiveEvents(self) -> list[Event]:
        events = []
        with self._get_dict_cursor() as cur:
            cur.execute("""
                SELECT id, evname, evdate, place, photo_amount, video_amount, created_by, created_at
                FROM event
                WHERE NOT EXISTS (
                    SELECT * FROM completed_event WHERE event_id = event.id
                ) AND NOT EXISTS (
                    SELECT * FROM canceled_event WHERE event_id = event.id
                )
            """)
            for row in cur.fetchall():
                eventID = UUID(hex=row['id'])
                chief = self.getEventChief(eventID)
                activists = self.getEventMembers(eventID)
                events.append(Event(
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
                ))
        return events
    
    def GetActiveEventByName(self, name: str) -> Event:
        with self._get_dict_cursor() as cur:
            cur.execute("""
                SELECT id, evname, evdate, place, photo_amount, video_amount, created_by, created_at
                FROM event
                WHERE evname = %s
                AND NOT EXISTS (
                    SELECT * FROM completed_event WHERE event_id = event.id
                )
                AND NOT EXISTS (
                    SELECT * FROM canceled_event WHERE event_id = event.id
                )
            """, (name,))
            row = cur.fetchone()
            if row:     
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
        return None
    
    def GetEventByName(self, name: str) -> Event:
        with self._get_dict_cursor() as cur:
            cur.execute("""
                SELECT id, evname, evdate, place, photo_amount, video_amount, created_by, created_at
                FROM event
                WHERE evname = %s
            """, (name,))
            row = cur.fetchone()
            if row:     
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
        return None
   
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
        acts = []
        with self._get_dict_cursor() as cur:
            cur.execute("""
                SELECT activist.id as acid, event_member.id as eid, chat_id, acname, valid
                FROM activist
                JOIN event_member ON event_member.activist_id = activist.id
                JOIN tg_user ON tg_user.id = activist.tg_user_id
                WHERE event_id = %s AND is_chief = false;
            """, (eventID.hex,))
            for row in cur.fetchall():
                act = Activist(ID=row['acid'], ChatID=row['chat_id'], Name=row['acname'], Valid=row['valid'])
                acts.append(EventActivist(ID=row['eid'], EventID=eventID, Activist=act))
        return acts

    def GetTgUser(self, chatID: int):
        with self._get_cursor() as cur:
            cur.execute("""
                SELECT id, chat_id, tg_username, agreed FROM tg_user WHERE chat_id = %s;
            """, (chatID,))
            row = cur.fetchone()
            if row:
                return TgUser(ID=row[0], ChatID=row[1], Username=row[2], Agreed=row[3])
        return None
    
    def GetTgUserByUName(self, username: str):
        with self._get_cursor() as cur:
            cur.execute("""
                SELECT id, chat_id, tg_username, agreed 
                FROM tg_user 
                WHERE tg_username = %s;
            """, (username,))
            row = cur.fetchone()
            if row:
                return TgUser(ID=row[0], ChatID=row[1], Username=row[2], Agreed=row[3])
        return None

    def GetActivistByTgUserID(self, tg_user_id: UUID):
        with self._get_cursor() as cur:
            cur.execute("""
                SELECT activist.id, chat_id, acname, valid
                FROM activist
                JOIN tg_user
                ON tg_user.id = activist.tg_user_id
                WHERE tg_user_id = %s
            """, (tg_user_id.hex,))
            row = cur.fetchone()
            if row:
                return Activist(ID=row[0], ChatID=row[1], Name=row[2], Valid=row[3])
        return None

    def PutActivist(self, tg_user_id: UUID, acname: str):
        with self._get_cursor() as cur:
            cur.execute("""
                INSERT INTO activist (id, tg_user_id, acname, valid) 
                VALUES (gen_random_uuid(), %s, %s, True)
            """, (tg_user_id.hex, acname))

    def UpdateValidActivist(self, id_act: UUID, funcUpdate):
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT ac.id, tu.chat_id, ac.acname, ac.valid
                    FROM tg_user tu
                    JOIN activist ac
                    ON tu.id = ac.tg_user_id
                    WHERE ac.id = %s
                """, (id_act.hex,))
                row = cur.fetchone()
                act = Activist(ID=row[0], ChatID=row[1], Name=row[2], Valid=row[3])
                newAct = funcUpdate(act)
                cur.execute("""
                    UPDATE activist
                    SET acname = %s, valid = %s
                    WHERE id = %s
                """, (newAct.Name, newAct.Valid, id_act.hex))
                conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.pool.putconn(conn)
        
    def GetEventByID(self, id: UUID) -> Event:
        with self._get_dict_cursor() as cur:
            cur.execute("""
                SELECT id, evname, evdate, place, photo_amount, video_amount, created_by, created_at
                FROM event
                WHERE id = %s
            """, (id.hex,))
            row = cur.fetchone()
            if row:
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
        return None

    def GetAllNotDoneNotifs(self) -> list[BaseNotification]:
        notifsRes = []
        with self._get_dict_cursor() as cur:
            cur.execute("""
                SELECT n.id as notif_id, n.extra_text, n.send_time, n.type_notif, ne.event_id as event_id
                FROM notifications n
                LEFT JOIN notif_event ne
                ON ne.notif_id = n.id
                WHERE n.done = FALSE;
            """)
            
            for r in cur.fetchall():
                notifID = UUID(hex=r['notif_id'])
                chatIDs = []
                cur2 = conn.cursor()
                cur2.execute("""
                    SELECT chat_id
                    FROM notif_tguser nu
                    JOIN tg_user u
                    ON nu.tguser_id = u.id
                    WHERE nu.notif_id = %s; 
                """, (r['notif_id'],))
                chatIDs = [int(row[0]) for row in cur2.fetchall()]
                cur2.close()
                
                event = None
                if r['event_id'] is not None:
                    event = self.GetEventByID(UUID(hex=r['event_id']))

                notification = NotifRegistryBase.Create(
                    r['type_notif'],
                    id=notifID,
                    text=r['extra_text'],
                    notifyTime=r['send_time'],
                    ChatIDs=chatIDs,
                    event=event
                )
                notifsRes.append(notification)
        return notifsRes

    def PutNotification(self, notif: BaseNotification):
        type_notif = notif.TYPE
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO notifications (id, extra_text, send_time, type_notif, done, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (notif.ID.hex, notif.Text, notif.NotifyTime, type_notif, False, datetime.now()))
                
                for chatID in notif.ChatIDs:
                    tgUser = self.GetTgUser(chatID)
                    if tgUser:
                        cur.execute("""
                            INSERT INTO notif_tguser (notif_id, tguser_id)
                            VALUES (%s, %s)
                        """, (notif.ID.hex, tgUser.ID.hex))

                if isinstance(notif, BaseNotifWithEvent):
                    cur.execute("""
                        INSERT INTO notif_event (notif_id, event_id)
                        VALUES (%s, %s)
                    """, (notif.ID.hex, notif.GetEventID().hex))
                
                conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.pool.putconn(conn)

    def SetDoneNotification(self, notifID: UUID):
        with self._get_cursor() as cur:
            cur.execute("""
                UPDATE notifications
                SET done = TRUE
                WHERE id = %s;
            """, (notifID.hex,))

    def RemoveNotification(self, notifID: UUID):
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    DELETE FROM notif_event
                    WHERE notif_id = %s;
                """, (notifID.hex,))
                cur.execute("""
                    DELETE FROM notif_tguser
                    WHERE notif_id = %s;
                """, (notifID.hex,))
                cur.execute("""
                    DELETE FROM notifications
                    WHERE id = %s;
                """, (notifID.hex,))
                conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.pool.putconn(conn)

    def GetEventsByActivistID(self, ActivistID: UUID) -> list[EventForActivist]:
        events = []
        with self._get_cursor() as cur:
            cur.execute("""
                SELECT e.id AS event_id, e.evname, e.evdate, e.photo_amount, e.video_amount
                FROM event_member em
                JOIN event e ON em.event_id = e.id
                WHERE em.activist_id = %s
            """, (ActivistID.hex,))
            
            for row in cur.fetchall():
                event_id = row[0]
                chief = self.GetTgUserActivistByActivistID(self.getEventChief(UUID(hex=event_id)).Activist.ID)
                events.append(EventForActivist( 
                    ID=UUID(hex=event_id),
                    Name=row[1],  
                    Date=row[2], 
                    Chief=chief, 
                    PhotoCount=row[3],
                    VideoCount=row[4]
                ))
        return events
    
    def GetActiveEventsByActivistID(self, ActivistID: UUID) -> list[EventForActivist]:
        events = []
        with self._get_cursor() as cur:
            cur.execute("""
                SELECT e.id AS event_id, e.evname, e.evdate, e.photo_amount, e.video_amount
                FROM event_member em
                JOIN event e ON em.event_id = e.id
                WHERE em.activist_id = %s AND NOT EXISTS (
                    SELECT * FROM completed_event WHERE event_id = e.id
                )
                AND NOT EXISTS (
                    SELECT * FROM canceled_event WHERE event_id = e.id
                );
            """, (ActivistID.hex,))

            for row in cur.fetchall():
                event_id = row[0]
                chief = self.GetTgUserActivistByActivistID(self.getEventChief(UUID(hex=event_id)).Activist.ID)
                events.append(EventForActivist( 
                    ID=UUID(hex=event_id),
                    Name=row[1],  
                    Date=row[2], 
                    Chief=chief, 
                    PhotoCount=row[3],
                    VideoCount=row[4]
                ))
        return events

    def GetTgUserActivistByActivistID(self, ActivistID: UUID) -> TgUserActivist:
        with self._get_cursor() as cur:
            cur.execute("""
                SELECT a.tg_user_id, a.acname, a.valid, t.chat_id, t.tg_username, t.agreed
                FROM activist a
                JOIN tg_user t ON a.tg_user_id = t.id
                WHERE a.id = %s
            """, (ActivistID.hex,))
            result = cur.fetchone()
            if result:
                return TgUserActivist(
                    IDTgUser=UUID(hex=result[0]),
                    IDActivist=ActivistID,
                    ChatID=result[3],
                    Username=result[4],
                    Name=result[1],
                    Valid=result[2],
                    Agreed=result[5]
                )
        return None

    def GetEventMemberByActivist(self, event_id: UUID, activist_id: UUID) -> EventActivist:
        with self._get_cursor() as cur:
            cur.execute("""
                SELECT activist.id, event_member.id, tg_user.chat_id, acname, valid
                FROM activist JOIN tg_user ON activist.tg_user_id = tg_user.id
                JOIN event_member ON event_member.activist_id = activist.id
                WHERE event_member.event_id = %s AND activist.id = %s;
            """, (event_id.hex, activist_id.hex))
            result = cur.fetchone()
            if result:
                return EventActivist(
                    ID=UUID(hex=result[1]),
                    EventID=event_id,
                    Activist=Activist(
                        ID=UUID(hex=result[0]),
                        ChatID=result[2],
                        Name=result[3],
                        Valid=result[4]
                    )
                )
        return None
    
    def GetActiveEventByNameForActivist(self, name: str, activistID: UUID) -> EventForActivist:
        with self._get_cursor() as cur:
            cur.execute("""
                SELECT e.id AS event_id, e.evname, e.evdate, e.photo_amount, e.video_amount
                FROM event_member em
                JOIN event e ON em.event_id = e.id
                WHERE em.activist_id = %s AND e.evname = %s AND NOT EXISTS (
                    SELECT * FROM completed_event WHERE event_id = e.id
                )
                AND NOT EXISTS (
                    SELECT * FROM canceled_event WHERE event_id = e.id
                );
            """, (activistID.hex, name))
            row = cur.fetchone()
            if row:
                event_id = row[0]
                chief = self.GetTgUserActivistByActivistID(self.getEventChief(UUID(hex=event_id)).Activist.ID)
                return EventForActivist( 
                    ID=UUID(hex=event_id),
                    Name=row[1],  
                    Date=row[2], 
                    Chief=chief, 
                    PhotoCount=row[3],
                    VideoCount=row[4]
                )
        return None
    
    def CreateReport(self, report: Report):
        evact = self.GetEventMemberByActivist(report.EventID, report.Activist.ID)
        if not evact:
            raise ValueError("Event member not found")
            
        with self._get_cursor() as cur:
            cur.execute("""
                INSERT INTO report (id, event_member_id, report_type, url, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (report.ID.hex, evact.ID.hex, report.Type, report.URL, report.CreatedAt))

