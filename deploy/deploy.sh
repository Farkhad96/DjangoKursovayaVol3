#!/bin/bash
set -euo pipefail

DEPLOY_PATH="${DEPLOY_PATH:-/opt/habits-tracker}"
COMPOSE_FILE="docker-compose.prod.yml"

cd "$DEPLOY_PATH"

git fetch origin main
git reset --hard origin/main

cat > .env <<EOF
SECRET_KEY=${SECRET_KEY}
DEBUG=False
ALLOWED_HOSTS=${ALLOWED_HOSTS}
CORS_ALLOWED_ORIGINS=${CORS_ALLOWED_ORIGINS}
CSRF_TRUSTED_ORIGINS=${CSRF_TRUSTED_ORIGINS}
POSTGRES_DB=${POSTGRES_DB}
POSTGRES_USER=${POSTGRES_USER}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
POSTGRES_HOST=db
POSTGRES_PORT=5432
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
EOF

docker compose -f "$COMPOSE_FILE" pull --ignore-buildable || true
docker compose -f "$COMPOSE_FILE" up -d --build --remove-orphans
docker image prune -f

echo "Deploy completed successfully."
