# Трекер полезных привычек

Бэкенд SPA-приложения для отслеживания полезных привычек по методологии «Атомных привычек».

## Стек

- Python 3.12 + Django 5 + Django REST Framework
- PostgreSQL / SQLite
- JWT-авторизация (SimpleJWT)
- Celery + Redis (напоминания в Telegram)
- Docker + Docker Compose
- drf-spectacular (документация API)

## Запуск через Docker Compose (рекомендуется)

### 1. Подготовка

```bash
cp .env.template .env
```

Отредактируйте `.env`: задайте `SECRET_KEY` и `TELEGRAM_BOT_TOKEN`.

> **Важно:** `.env.template` содержит настройки для Docker (PostgreSQL, Redis по именам сервисов). Для локального запуска без Docker удалите строку `POSTGRES_HOST` — будет использоваться SQLite, а Redis — `localhost`.

### 2. Запуск всех сервисов

```bash
docker compose up --build
```

Поднимаются сервисы:

| Сервис | Описание | Доступ |
|--------|----------|--------|
| `web` | Django API | http://localhost:8000 |
| `db` | PostgreSQL | только внутри сети (`expose`) |
| `redis` | Брокер Celery | только внутри сети (`expose`) |
| `celery` | Воркер фоновых задач | — |
| `celery-beat` | Планировщик напоминаний | — |

Данные PostgreSQL и Redis сохраняются в именованных volumes: `postgres_data`, `redis_data`.

### 3. Остановка

```bash
docker compose down
```

Чтобы удалить и данные БД:

```bash
docker compose down -v
```

## Локальный запуск без Docker

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.template .env
```

Для локального запуска уберите или закомментируйте `POSTGRES_HOST` в `.env` — будет использоваться SQLite.

```bash
python manage.py migrate
python manage.py runserver
```

Celery (нужен локальный Redis):

```bash
celery -A config worker -l info
celery -A config beat -l info
```

## Документация API

- Swagger: http://localhost:8000/docs/
- ReDoc: http://localhost:8000/redoc/
- Schema: http://localhost:8000/schema/

## Эндпоинты

| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/users/register/` | Регистрация |
| POST | `/users/token/` | Авторизация (JWT) |
| POST | `/users/token/refresh/` | Обновление токена |
| PATCH | `/users/telegram/` | Привязка Telegram chat ID |
| GET | `/habits/` | Список привычек пользователя |
| POST | `/habits/` | Создание привычки |
| GET/PATCH/DELETE | `/habits/{id}/` | CRUD привычки |
| GET | `/habits/public/` | Публичные привычки |

## Telegram

1. Создайте бота через [@BotFather](https://t.me/BotFather).
2. Укажите токен в `.env` → `TELEGRAM_BOT_TOKEN`.
3. Привяжите chat ID: `PATCH /users/telegram/` с телом `{"telegram_chat_id": "ваш_id"}`.

## Тесты

```bash
coverage run --source='habits,users,telegram_bot,config' manage.py test
coverage report --omit='*/migrations/*,*/tests/*,manage.py,config/wsgi.py,config/asgi.py'
```
## Вопросы и ответы
Этот раздел пока пустой

