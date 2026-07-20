from django.conf import settings
from django.db import models

from habits.validators import (
    validate_execution_time,
    validate_habit_fields,
    validate_periodicity,
)


class Habit(models.Model):
    """Модель привычки."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="habits",
        verbose_name="Пользователь",
    )
    place = models.CharField(max_length=200, verbose_name="Место")
    time = models.TimeField(verbose_name="Время")
    action = models.CharField(max_length=200, verbose_name="Действие")
    is_pleasant = models.BooleanField(
        default=False, verbose_name="Признак приятной привычки"
    )
    related_habit = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="linked_habits",
        verbose_name="Связанная привычка",
    )
    periodicity = models.PositiveSmallIntegerField(
        default=1,
        validators=[validate_periodicity],
        verbose_name="Периодичность (дни)",
    )
    reward = models.CharField(
        max_length=200, blank=True, null=True, verbose_name="Вознаграждение"
    )
    execution_time = models.PositiveSmallIntegerField(
        validators=[validate_execution_time],
        verbose_name="Время на выполнение (сек)",
    )
    is_public = models.BooleanField(
        default=False, verbose_name="Признак публичности"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ["id"]

    def __str__(self):
        return f"{self.action} в {self.time} в {self.place}"

    def clean(self):
        super().clean()
        validate_habit_fields(self)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
