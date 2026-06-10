from datetime import time

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from habits.models import Habit

User = get_user_model()


class HabitAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user@example.com",
            email="user@example.com",
            password="testpass123",
        )
        self.other_user = User.objects.create_user(
            username="other@example.com",
            email="other@example.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.user)
        self.pleasant = Habit.objects.create(
            user=self.user,
            place="ванная",
            time=time(21, 0),
            action="принять ванну",
            is_pleasant=True,
            execution_time=30,
        )

    def test_create_habit(self):
        url = reverse("habit-list")
        data = {
            "place": "парк",
            "time": "18:00:00",
            "action": "гулять",
            "execution_time": 60,
            "reward": "чай",
            "periodicity": 1,
            "is_public": False,
            "is_pleasant": False,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.filter(user=self.user).count(), 2)

    def test_list_only_own_habits(self):
        Habit.objects.create(
            user=self.other_user,
            place="офис",
            time=time(9, 0),
            action="работать",
            execution_time=60,
        )
        response = self.client.get(reverse("habit-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_pagination_limit_five(self):
        for i in range(6):
            Habit.objects.create(
                user=self.user,
                place=f"место{i}",
                time=time(10, i % 24),
                action=f"действие{i}",
                execution_time=30,
            )
        response = self.client.get(reverse("habit-list"))
        self.assertEqual(len(response.data["results"]), 5)
        self.assertEqual(response.data["count"], 7)

    def test_update_own_habit(self):
        habit = Habit.objects.create(
            user=self.user,
            place="парк",
            time=time(18, 0),
            action="гулять",
            execution_time=60,
        )
        url = reverse("habit-detail", kwargs={"pk": habit.pk})
        response = self.client.patch(url, {"place": "лес"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        habit.refresh_from_db()
        self.assertEqual(habit.place, "лес")

    def test_cannot_update_other_habit(self):
        habit = Habit.objects.create(
            user=self.other_user,
            place="офис",
            time=time(9, 0),
            action="работать",
            execution_time=60,
        )
        url = reverse("habit-detail", kwargs={"pk": habit.pk})
        response = self.client.patch(url, {"place": "лес"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_own_habit(self):
        habit = Habit.objects.create(
            user=self.user,
            place="парк",
            time=time(18, 0),
            action="гулять",
            execution_time=60,
        )
        url = reverse("habit-detail", kwargs={"pk": habit.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_public_habits_list(self):
        Habit.objects.create(
            user=self.other_user,
            place="парк",
            time=time(18, 0),
            action="бегать",
            execution_time=60,
            is_public=True,
        )
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse("public-habits"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_validation_reward_and_related(self):
        url = reverse("habit-list")
        data = {
            "place": "парк",
            "time": "18:00:00",
            "action": "гулять",
            "execution_time": 60,
            "reward": "чай",
            "related_habit": self.pleasant.pk,
            "periodicity": 1,
            "is_pleasant": False,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_execution_time_validation(self):
        url = reverse("habit-list")
        data = {
            "place": "парк",
            "time": "18:00:00",
            "action": "гулять",
            "execution_time": 150,
            "periodicity": 1,
            "is_pleasant": False,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_periodicity_validation(self):
        url = reverse("habit-list")
        data = {
            "place": "парк",
            "time": "18:00:00",
            "action": "гулять",
            "execution_time": 60,
            "periodicity": 10,
            "is_pleasant": False,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
