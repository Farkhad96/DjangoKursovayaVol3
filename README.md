# Employee Task Tracker (Django + DRF)

Серверное приложение трекера задач сотрудников на Python 3.11, Django REST Framework и PostgreSQL.

## Стек

- Python 3.11
- Django 5.1 + DRF
- PostgreSQL
- drf-spectacular (Swagger/ReDoc)
- Docker + Docker Compose

## Структура

- `tracker/` — доменная модель Employee/Task, CRUD API, специальные endpoint'ы.
- `config/` — настройки проекта, роутинг, Swagger/ReDoc.
- `users/`, `habits/`, `telegram_bot/` — существующие модули проекта.

## Запуск локально

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.template .env
python manage.py migrate
python manage.py runserver
```

## Запуск в Docker

```bash
cp .env.template .env
docker compose up --build
```

Сервис будет доступен на `http://localhost:8000`.

## API документация

- Swagger UI: `http://localhost:8000/docs/`
- ReDoc: `http://localhost:8000/redoc/`
- OpenAPI schema: `http://localhost:8000/schema/`

## Основные endpoint'ы

### CRUD сотрудников

- `GET/POST /api/employees/`
- `GET/PATCH/DELETE /api/employees/{id}/`

### CRUD задач

- `GET/POST /api/tasks/`
- `GET/PATCH/DELETE /api/tasks/{id}/`

Поля задачи:
- `title`
- `parent` (nullable, ссылка на родительскую задачу)
- `assignee` (nullable, FK на сотрудника)
- `deadline`
- `status` (`new`, `in_progress`, `blocked`, `done`, `canceled`)

### Спец endpoint: занятые сотрудники

- `GET /api/employees/busy/`

Возвращает сотрудников с задачами, отсортированных по убыванию количества **активных** задач.

Активные статусы: `new`, `in_progress`, `blocked`.

### Спец endpoint: важные задачи

- `GET /api/tasks/important/`

Возвращает задачи со статусом `new` без исполнителя, от которых зависят задачи в статусах `in_progress`/`blocked`, с рекомендацией сотрудников:
1. Наименее загруженный сотрудник.
2. Исполнитель родительской задачи (если его активная нагрузка не больше чем на 2 задачи выше минимальной).

Формат элемента ответа:

```json
{
  "важная_задача": "Подготовить ТЗ",
  "срок": "2026-07-20T12:00:00Z",
  "ФИО_сотрудника": ["Иван Иванов", "Петр Петров"]
}
```

## Тесты и покрытие

```bash
python manage.py test
coverage run --source='.' manage.py test
coverage report
```

Текущее покрытие тестами: `96%`.
