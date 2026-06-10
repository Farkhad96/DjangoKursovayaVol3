from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from users.auth import EmailTokenObtainPairSerializer
from users.models import UserProfile
from users.serializers import TelegramChatSerializer, UserRegistrationSerializer


@extend_schema(summary="Регистрация пользователя")
class UserRegistrationView(generics.CreateAPIView):
    """Регистрация нового пользователя."""

    serializer_class = UserRegistrationSerializer
    permission_classes = (AllowAny,)


@extend_schema(summary="Авторизация (получение JWT-токена)")
class CustomTokenObtainPairView(TokenObtainPairView):
    """Авторизация пользователя и выдача JWT-токена."""

    serializer_class = EmailTokenObtainPairSerializer


@extend_schema(summary="Привязка Telegram chat ID")
class TelegramChatView(generics.UpdateAPIView):
    """Привязка Telegram chat ID к профилю пользователя."""

    serializer_class = TelegramChatSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ["patch"]

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile.telegram_chat_id = serializer.validated_data["telegram_chat_id"]
        profile.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
