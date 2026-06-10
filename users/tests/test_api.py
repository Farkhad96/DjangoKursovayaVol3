from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class UserAPITestCase(APITestCase):
    def test_registration(self):
        url = reverse("register")
        data = {"email": "new@example.com", "password": "testpass123"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="new@example.com").exists())

    def test_login(self):
        User.objects.create_user(
            username="user@example.com",
            email="user@example.com",
            password="testpass123",
        )
        url = reverse("token_obtain")
        response = self.client.post(
            url, {"email": "user@example.com", "password": "testpass123"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_telegram_chat_id_update(self):
        user = User.objects.create_user(
            username="user@example.com",
            email="user@example.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=user)
        url = reverse("telegram_chat")
        response = self.client.patch(url, {"telegram_chat_id": "123456"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertEqual(user.profile.telegram_chat_id, "123456")
