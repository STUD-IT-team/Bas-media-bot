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