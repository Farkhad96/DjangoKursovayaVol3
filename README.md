# Employee Task Tracker (Django + DRF)

Серверное приложение трекера задач сотрудников на Python 3.11, Django REST Framework и PostgreSQL.

## Стек

- Python 3.12 + Django 5 + Django REST Framework
- PostgreSQL, Redis, Celery
- Gunicorn + Nginx (production)
- Docker + Docker Compose
- GitHub Actions (CI/CD)
- Yandex Cloud (деплой на ВМ)

---

## Локальная разработка

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.template .env
```

Для локального запуска **удалите** `POSTGRES_HOST` из `.env` — будет использоваться SQLite.

```bash
python manage.py migrate
python manage.py runserver
```

### Docker (разработка)

```bash
cp .env.template .env
docker compose up --build
```

API: http://localhost:8000/docs/

---

## Деплой на Yandex Cloud

### 1. Создание виртуальной машины

1. В [Yandex Cloud Console](https://console.cloud.yandex.ru/) создайте ВМ:
   - **ОС:** Ubuntu 22.04 LTS
   - **Платформа:** Intel Ice Lake
   - **Диск:** 10+ ГБ SSD
   - **Публичный IP:** включить

2. **Группа безопасности** (Security Groups):
   | Порт | Протокол | Источник | Назначение |
   |------|----------|----------|------------|
   | 22 | TCP | Ваш IP / 0.0.0.0/0 | SSH |
   | 80 | TCP | 0.0.0.0/0 | HTTP (Nginx) |
   | 443 | TCP | 0.0.0.0/0 | HTTPS (опционально) |

   Все остальные порты **закрыты**. PostgreSQL (5432) и Redis (6379) доступны только внутри Docker-сети.

3. **SSH-ключ:** при создании ВМ добавьте свой публичный ключ (`~/.ssh/id_rsa.pub`).

### 2. Первичная настройка сервера

```bash
ssh ubuntu@<PUBLIC_IP>

# На сервере:
sudo bash deploy/server-setup.sh https://github.com/<user>/<repo>.git
```

Скрипт установит Docker, настроит UFW (открыты только 22 и 80) и клонирует репозиторий в `/opt/habits-tracker`.

### 3. GitHub Secrets

В репозитории: **Settings → Secrets and variables → Actions → New repository secret**

| Secret | Описание | Пример |
|--------|----------|--------|
| `SSH_PRIVATE_KEY` | Приватный SSH-ключ (содержимое `id_rsa`) | `-----BEGIN OPENSSH...` |
| `SERVER_HOST` | Публичный IP ВМ Yandex Cloud | `51.250.x.x` |
| `SERVER_USER` | Пользователь SSH | `ubuntu` |
| `DEPLOY_PATH` | Путь к проекту на сервере | `/opt/habits-tracker` |
| `SECRET_KEY` | Django secret key (50+ символов) | случайная строка |
| `ALLOWED_HOSTS` | IP и домен через запятую | `51.250.x.x,your-domain.ru` |
| `CORS_ALLOWED_ORIGINS` | Адреса фронтенда | `https://your-frontend.com` |
| `CSRF_TRUSTED_ORIGINS` | Домен API с протоколом | `http://51.250.x.x` |
| `POSTGRES_DB` | Имя БД | `habits` |
| `POSTGRES_USER` | Пользователь БД | `habits` |
| `POSTGRES_PASSWORD` | Пароль БД | надёжный пароль |
| `TELEGRAM_BOT_TOKEN` | Токен Telegram-бота | от BotFather |

### 4. Первый деплой

```bash
# Локально — пуш в main запускает CI/CD автоматически
git push origin main
```

Или вручную на сервере:

```bash
cd /opt/habits-tracker
cp .env.template .env   # заполните значения
docker compose -f docker-compose.prod.yml up -d --build
```

### 5. Проверка

- API: `http://<PUBLIC_IP>/docs/`
- Авто-перезапуск: все сервисы в `docker-compose.prod.yml` имеют `restart: always`
- Логи: `docker compose -f docker-compose.prod.yml logs -f web nginx`

---

## CI/CD Pipeline (GitHub Actions)

Файл: `.github/workflows/ci-cd.yml`

```
push / PR → test → lint → build → deploy (только main)
```

| Этап | Что делает | Останавливает pipeline при ошибке |
|------|------------|-----------------------------------|
| **test** | Django-тесты + coverage ≥ 80% | да |
| **lint** | Ruff (PEP 8) | да |
| **build** | Сборка Docker-образа | да |
| **deploy** | SSH → `deploy/deploy.sh` → `docker compose up` | да |

Деплой выполняется **только** при push в `main`, после успешных test + lint + build.

---

## Production-архитектура

```
Интернет → Nginx (:80) → Gunicorn (:8000) → Django
                              ↓
                    PostgreSQL + Redis
                              ↓
                    Celery Worker + Beat
```

| Сервис | Доступ | Авто-перезапуск |
|--------|--------|-----------------|
| `nginx` | порт 80 (внешний) | `restart: always` |
| `web` (Gunicorn) | expose 8000 | `restart: always` |
| `db` (PostgreSQL) | expose 5432 + volume | `restart: always` |
| `redis` | expose 6379 + volume | `restart: always` |
| `celery` / `celery-beat` | внутренняя сеть | `restart: always` |

---

## Эндпоинты API

- `GET /api/employees/busy/`

## Тесты (локально)

```bash
pip install -r requirements-dev.txt
coverage run --source='habits,users,telegram_bot,config' manage.py test
coverage report --fail-under=80 \
  --omit='*/migrations/*,*/tests/*,manage.py,config/wsgi.py,config/asgi.py'
ruff check habits users telegram_bot config manage.py \
  --exclude habits/migrations,users/migrations
```

## Telegram

1. Создайте бота через [@BotFather](https://t.me/BotFather).
2. Укажите токен в `TELEGRAM_BOT_TOKEN` (GitHub Secret / `.env`).
3. Привяжите chat ID: `PATCH /users/telegram/` с телом `{"telegram_chat_id": "ваш_id"}`.
