from storage.pgredis import PostgresCredentials, RedisCredentials, PgRedisStorage
from utils.token import GetPgCredEnv, GetRedisCredEnv



pgcred = PostgresCredentials(**GetPgCredEnv())
redcred = RedisCredentials(**GetRedisCredEnv(), db=0)
try:
    storage = PgRedisStorage(pgcred, redcred)
    del storage
except Exception as e:
    print(f"Ошибка при создании хранилища: {str(e)}")
    exit(1)