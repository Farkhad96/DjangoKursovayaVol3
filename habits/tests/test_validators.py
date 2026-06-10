from django.core.exceptions import ValidationError
from django.test import TestCase

from habits.validators import (
    validate_execution_time,
    validate_habit_fields,
    validate_periodicity,
)


class ValidatorsTestCase(TestCase):
    def test_validate_execution_time_valid(self):
        validate_execution_time(120)

    def test_validate_execution_time_invalid(self):
        with self.assertRaises(ValidationError):
            validate_execution_time(121)

    def test_validate_periodicity_valid(self):
        for value in range(1, 8):
            validate_periodicity(value)

    def test_validate_periodicity_too_low(self):
        with self.assertRaises(ValidationError):
            validate_periodicity(0)

    def test_validate_periodicity_too_high(self):
        with self.assertRaises(ValidationError):
            validate_periodicity(8)

    def test_both_reward_and_related_habit(self):
        class FakeHabit:
            related_habit = object()
            reward = "test"
            is_pleasant = False

        with self.assertRaises(ValidationError):
            validate_habit_fields(FakeHabit())

    def test_pleasant_habit_with_reward(self):
        class FakeHabit:
            related_habit = None
            reward = "test"
            is_pleasant = True

        with self.assertRaises(ValidationError):
            validate_habit_fields(FakeHabit())

    def test_pleasant_habit_with_related(self):
        class FakeHabit:
            related_habit = object()
            reward = None
            is_pleasant = True

        with self.assertRaises(ValidationError):
            validate_habit_fields(FakeHabit())
