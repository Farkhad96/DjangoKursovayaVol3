from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации пользователя."""

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("id", "email", "password")
        extra_kwargs = {"email": {"required": True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["email"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user


class TelegramChatSerializer(serializers.Serializer):
    """Сериализатор для привязки Telegram chat ID."""

    telegram_chat_id = serializers.CharField(max_length=50)
