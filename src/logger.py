import logging
import os
import sys

LOGGING_KWARGS = {
    "format": "[%(levelname)s, %(asctime)s, %(filename)s] func %(funcName)s, line %(lineno)d: %(message)s;",
    "datefmt": "%d.%m.%Y %H:%M:%S",
    "stream": sys.stdout,
    "level": logging.INFO if (os.getenv("LOGGER_DEBUG", '0') != '1') else logging.DEBUG
}

logger = logging.getLogger("bas-bot-logger")
logging.basicConfig(**LOGGING_KWARGS)