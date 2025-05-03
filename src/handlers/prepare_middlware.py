from logger import logger
from middleware.agreement import AgreementMiddleware
from middleware.auth import AuthMiddleware
from middleware.log import LogMiddleware
from middleware.storage import StorageMiddleware
from storage import PgRedisStorage, pgcred, redcred


async def prepare_middleware(dp):
    dp.update.outer_middleware(LogMiddleware(logger))
    dp.update.outer_middleware(StorageMiddleware(PgRedisStorage, pgcred, redcred))
    dp.update.outer_middleware(AgreementMiddleware())
    dp.update.outer_middleware(AuthMiddleware())