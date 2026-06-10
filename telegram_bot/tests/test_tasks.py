from datetime import time
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from habits.models import Habit
from telegram_bot.tasks import send_habit_reminders, should_send_reminder
from users.models import UserProfile

User = get_user_model()


class TelegramTasksTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user@example.com",
            email="user@example.com",
            password="testpass123",
        )
        UserProfile.objects.filter(user=self.user).update(
            telegram_chat_id="12345"
        )

    def test_should_send_reminder_daily(self):
        habit = Habit.objects.create(
            user=self.user,
            place="парк",
            time=time(18, 0),
            action="гулять",
            execution_time=60,
            periodicity=1,
        )
        today = timezone.localdate()
        self.assertTrue(should_send_reminder(habit, today))

    def test_should_send_reminder_weekly(self):
        habit = Habit.objects.create(
            user=self.user,
            place="парк",
            time=time(18, 0),
            action="гулять",
            execution_time=60,
            periodicity=7,
        )
        today = habit.created_at.date()
        self.assertTrue(should_send_reminder(habit, today))

    @patch("telegram_bot.tasks.send_telegram_message")
    @patch("telegram_bot.tasks.timezone.localtime")
    def test_send_habit_reminders(self, mock_localtime, mock_send):
        habit_time = time(10, 30)
        mock_now = timezone.now().replace(
            hour=habit_time.hour, minute=habit_time.minute, second=0
        )
        mock_localtime.return_value = mock_now

        Habit.objects.create(
            user=self.user,
            place="парк",
            time=habit_time,
            action="гулять",
            execution_time=60,
            periodicity=1,
        )

        send_habit_reminders()
        mock_send.assert_called_once()

    @patch("telegram_bot.services.requests.post")
    def test_send_telegram_message_service(self, mock_post):
        from django.test import override_settings

        from telegram_bot.services import send_telegram_message

        mock_post.return_value.raise_for_status = lambda: None
        with override_settings(TELEGRAM_BOT_TOKEN="test-token"):
            result = send_telegram_message("123", "Привет")
        self.assertTrue(result)
        mock_post.assert_called_once()
