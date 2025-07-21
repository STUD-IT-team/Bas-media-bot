import os

def GetBotTokenEnv() -> str:
    return os.getenv('BOT_TOKEN')

def GetRedisCredEnv() -> dict:
    return {
        "host" : os.getenv('REDIS_HOST'),
        "port" : int(os.getenv('REDIS_PORT')),
        "user" : os.getenv('REDIS_USER'),
        "password" : os.getenv('REDIS_PASSWORD')
    }

def GetPgCredEnv() -> dict:
    return {
        "host" : os.getenv('PG_HOST'),
        "port" : int(os.getenv('PG_PORT')),
        "dbname" : os.getenv('PG_DB'),
        "user" : os.getenv('PG_USER'),
        "password" : os.getenv('PG_PASSWORD')
    }

def GetGoogleExportCredsEnv() -> dict:
    return {
        "credsFile" : os.getenv('GOOGLE_CREDS_FILE'),
        "spreadsheetId" : os.getenv('GOOGLE_SPREADSHEET_ID'),
        "pgcred" : {
            "host" : os.getenv('PG_HOST'),
            "port" : int(os.getenv('PG_PORT')),
            "dbname" : os.getenv('PG_DB'),
            "user" : os.getenv('PG_USER'),
            "password" : os.getenv('PG_PASSWORD')
        }
    }