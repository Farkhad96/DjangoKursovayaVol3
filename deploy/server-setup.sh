#!/bin/bash
set -euo pipefail

# Первичная настройка ВМ в Yandex Cloud (Ubuntu 22.04+).
# Запускать на сервере под пользователем с sudo.

DEPLOY_PATH="/opt/habits-tracker"
REPO_URL="${1:-}"

if [ -z "$REPO_URL" ]; then
  echo "Usage: sudo bash server-setup.sh <git-repo-url>"
  exit 1
fi

apt-get update
apt-get install -y ca-certificates curl git ufw

# Docker
if ! command -v docker >/dev/null 2>&1; then
  install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
  chmod a+r /etc/apt/keyrings/docker.asc
  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
    $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
    > /etc/apt/sources.list.d/docker.list
  apt-get update
  apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
fi

systemctl enable docker
systemctl start docker

# Firewall: SSH + HTTP, остальное закрыто
ufw default deny incoming
ufw default allow outgoing
ufw allow OpenSSH
ufw allow 80/tcp
ufw --force enable

# Каталог проекта
mkdir -p "$DEPLOY_PATH"
if [ ! -d "$DEPLOY_PATH/.git" ]; then
  git clone "$REPO_URL" "$DEPLOY_PATH"
fi

chown -R "${SUDO_USER:-$USER}:${SUDO_USER:-$USER}" "$DEPLOY_PATH"

echo "Server setup complete."
echo "Next steps:"
echo "1. Create .env in $DEPLOY_PATH (or use GitHub Actions deploy)"
echo "2. Run: cd $DEPLOY_PATH && docker compose -f docker-compose.prod.yml up -d --build"
