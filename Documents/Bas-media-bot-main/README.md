# BAS Media Bot

Бот для агрегации и ведения отчётов мероприятий **Bauman Active Sports**.

**WARNING**: Инструкция написана под Linux системы, если у вас винда, то досвидания.

## Команды

W.I.P.

## Зависимости

Необходимо: docker, docker-compose, git.

Рекомендуется: Excalidraw - для возможности просмотра графов из docs.

## Упрощённое древо проекта

```
.
├── creds - Креды для работы с гугл таблицей.
├── data - Вольюмы контейнеров.
├── deployment - Файлы необходимые для деплоя.
│   ├── docker-compose.yaml - Компоуз.
│   ├── bot.env - Переменные среды для контейнера бота.
│   ├── postgres.env - Переменные среды для контейнера базы.
│   ├── migrator.env - Переменные среды для контейнера мигратора.
│   ├── redis.env - Переменные среды для контейнера редиса.
│   └── ...
├── docs - Документация.
├── migrations - Миграции баз данных.
├── script - Shell скрипты.
├── src - Исходный код.
│   ├── handlers - Обработчики событий.
│   ├── keyboards - Шаблоны клавиатур.
│   ├── middleware - Мидлвари.
│   ├── models - Доменные модели.
│   ├── pkg - Сторонние пакеты.
│   ├── storage - Работа с базой данных.
│   ├── utils - Дополнительные уттилиты.
│   ├── requirements.txt - Файл с зависимостями для pip.
│   ├── run.py - Файл точки входа.
│   └── ...
└── README.md - Этот самый файл).
```

## Формат env файлов

### bot.env

```
BOT_TOKEN = ID:TOKEN

PG_HOST = db-bas
PG_DB = bas
PG_PORT = 5432
PG_USER = <DB_USER>
PG_PASSWORD = <DB_PASSWORD>

REDIS_HOST = redis-bas
REDIS_PORT = 6379
REDIS_USER = <RD_USER>
REDIS_PASSWORD = <RD_USER_PASSWORD>
```

### migrator.env

```
DB_HOST = db-bas
DB_NAME = bas
DB_PORT = 5432
DB_USER = <DB_USER>
DB_PASSWORD = <DB_PASSWORD>
```

### postgres.env

```
POSTGRES_HOST = db-bas
POSTGRES_DB = bas
POSTGRES_PORT = 5432
POSTGRES_USER = <DB_USER>
POSTGRES_PASSWORD = <DB_PASSWORD>
```

### redis.env

```
REDIS_USER = <RD_USER>
REDIS_PASSWORD = <RD_PASSWORD>
REDIS_USER_PASSWORD = <RD_USER_PASSWORD>
```

## Разработка

Для начала необходимо склонировать репу, и настроить `git config`.
Крайне рекомендуется предварительно настроить себе [SSH ключ на GitHub](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account).

Затем требуется создать все необходимые env файлы в папке deployments.
Шаблоны env файлов имеются выше. **! НЕ ЗАБУДЬ ЗАПОЛНИТЬ ЭТИ ФАЙЛЫ КОРРЕКТНЫМИ ЗНАЧЕНИЯМИ!**

Для каждого изменения нужно создавать отдельную ветку с понятным названием.
Название ветви должно отображать конкретную функцию или модуль над которым вы работаете.

Не нужно делать разные по тематике работы в одной ветви, Сделайте для них две отдельные.



## Деплой

Для начала необходимо перейти в директорию deployments. На этот момент у вас уже должны быть созданы все env файлы, и создан бот.
(Боты в Telegram создаются с помощью бота **[@BotFather](https://t.me/BotFather)**)

Сборка и запуск (В detached режиме):
```bash
docker compose up --build -d
```

Cборка и запуск (В attached режиме):
```bash
docker compose up --build
```

Запуск без сборки (detached):
```bash
docker compose up -d
```

Думаю принцип понятен.

Если у тебя сложности с docker, читай [документацию](https://docs.docker.com) и [ещё](https://docs.docker.com/compose/).