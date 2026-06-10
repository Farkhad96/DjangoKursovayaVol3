from datetime import time

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from habits.models import Habit

User = get_user_model()


class HabitModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password="testpass123",
        )
        self.pleasant = Habit.objects.create(
            user=self.user,
            place="ванная",
            time=time(21, 0),
            action="принять ванну",
            is_pleasant=True,
            execution_time=30,
        )

    def test_create_useful_habit_with_reward(self):
        habit = Habit.objects.create(
            user=self.user,
            place="парк",
            time=time(18, 0),
            action="гулять",
            execution_time=60,
            reward="десерт",
        )
        self.assertEqual(habit.reward, "десерт")

    def test_create_useful_habit_with_related(self):
        habit = Habit.objects.create(
            user=self.user,
            place="парк",
            time=time(18, 0),
            action="гулять",
            execution_time=60,
            related_habit=self.pleasant,
        )
        self.assertEqual(habit.related_habit, self.pleasant)

    def test_cannot_have_reward_and_related(self):
        with self.assertRaises(ValidationError):
            Habit.objects.create(
                user=self.user,
                place="парк",
                time=time(18, 0),
                action="гулять",
                execution_time=60,
                reward="десерт",
                related_habit=self.pleasant,
            )

    def test_related_must_be_pleasant(self):
        useful = Habit.objects.create(
            user=self.user,
            place="офис",
            time=time(9, 0),
            action="работать",
            execution_time=60,
        )
        with self.assertRaises(ValidationError):
            Habit.objects.create(
                user=self.user,
                place="парк",
                time=time(18, 0),
                action="гулять",
                execution_time=60,
                related_habit=useful,
            )

    def test_str_representation(self):
        habit = Habit.objects.create(
            user=self.user,
            place="парк",
            time=time(18, 0),
            action="гулять",
            execution_time=60,
        )
        self.assertIn("гулять", str(habit))
