from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    """Профиль пользователя с данными для Telegram."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    telegram_chat_id = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="Telegram chat ID"
    )

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self):
        return f"Профиль {self.user}"
