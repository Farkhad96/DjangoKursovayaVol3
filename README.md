# Трекер полезных привычек

Бэкенд SPA-приложения для отслеживания полезных привычек по методологии «Атомных привычек».

## Стек

- Python 3.10+
- Django 5 + Django REST Framework
- JWT-авторизация (SimpleJWT)
- Celery + Redis (напоминания в Telegram)
- drf-spectacular (документация API)

## Быстрый старт

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.template .env
python manage.py migrate
python manage.py runserver
```

## Celery

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

## Тесты

```bash
coverage run --source='.' manage.py test
coverage report
```
## Вопросы и ответы
Этот раздел пока пустой

