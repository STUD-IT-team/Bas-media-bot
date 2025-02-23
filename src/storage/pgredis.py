from pydantic import BaseModel
from storage.storage import BaseStorage
from storage import domain
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

    def PutTgUser(self, chat_id : int, username : str):
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO tg_user (id, chat_id, tg_username) VALUES (gen_random_uuid (), %s, %s) ON CONFLICT (chat_id) DO UPDATE SET tg_username = EXCLUDED.tg_username;
        """, (chat_id, username))
        self.conn.commit()

    def GetActivistByChatID(self, chatID : int) -> domain.Activist:

        cur = self.conn.cursor()

        cur.execute("""
            SELECT activist.id, chat_id, acname, valid FROM activist JOIN tg_user ON tg_user.id = activist.tg_user_id WHERE chat_id = %s AND valid = true;
        """, (chatID,))

        row = cur.fetchone()
        cur.close()
        
        act = None
        if row:
            act = domain.Activist(ID=row[0], ChatID=row[1], Name=row[2], Valid=row[3])
        return act
    
    def GetAdminByChatID(self, chatID : int) -> domain.Admin:
        cur = self.conn.cursor()

        cur.execute("""
            SELECT tg_admin.id, chat_id FROM tg_admin JOIN tg_user ON tg_user.id = tg_admin.tg_user_id WHERE chat_id = %s;
        """, (chatID,))

        row = cur.fetchone()
        cur.close()
        
        adm = None
        if row:
            adm = domain.Admin(ID=row[0], ChatID=row[1])
        return adm

        



