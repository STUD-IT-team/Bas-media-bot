# Bas-media-bot

Бот медиа BAS

## Команды

- /start - Начать работу

## Дерево проекта

```
.
├── creds
│   └── credentials.json  // google cloud - Service Account
├── data
├── deployment
│   ├── app.env
│   ├── docker-compose.yaml
│   ├── migrator.env
│   └── postgres.env
├── migrations
│   ├── 001_init.sql
│   ├── Dockerfile
│   └── entrypoint.sh
├── README.md
├── script
│   └── gen_requirements.sh
└── src
```

## app.env

```
BOT_TOKEN
DB_HOST
DB_USER
DB_PASSWORD
DB_NAME
DB_PORT
SPREADSHEET_ID
```

## migrator.env

```
DB_HOST
DB_USER
DB_PASSWORD
DB_NAME
```

## postgrs.env

```
POSTGRES_HOST
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_DB
```