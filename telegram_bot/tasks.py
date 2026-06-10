from celery import shared_task
from django.utils import timezone

from habits.models import Habit
from telegram_bot.services import send_telegram_message


def should_send_reminder(habit, today):
    """Проверка, нужно ли отправлять напоминание сегодня."""
    days_since_creation = (today - habit.created_at.date()).days
    return days_since_creation % habit.periodicity == 0


@shared_task
def send_habit_reminders():
    """Отправка напоминаний о привычках по расписанию."""
    now = timezone.localtime()
    current_time = now.time().replace(second=0, microsecond=0)
    today = now.date()

    habits = Habit.objects.filter(
        time=current_time,
        is_pleasant=False,
    ).select_related("user", "user__profile", "related_habit")

    for habit in habits:
        if not should_send_reminder(habit, today):
            continue

        profile = getattr(habit.user, "profile", None)
        if not profile or not profile.telegram_chat_id:
            continue

        message = (
            f"Напоминание: я буду {habit.action} в {habit.time.strftime('%H:%M')} "
            f"в {habit.place}."
        )
        if habit.related_habit:
            message += (
                f"\nПосле этого: {habit.related_habit.action} "
                f"в {habit.related_habit.place}."
            )
        elif habit.reward:
            message += f"\nВознаграждение: {habit.reward}."

        send_telegram_message(profile.telegram_chat_id, message)
