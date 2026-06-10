from rest_framework import serializers

from habits.models import Habit
from habits.validators import validate_habit_fields


class HabitSerializer(serializers.ModelSerializer):
    """Сериализатор привычки."""

    class Meta:
        model = Habit
        fields = (
            "id",
            "place",
            "time",
            "action",
            "is_pleasant",
            "related_habit",
            "periodicity",
            "reward",
            "execution_time",
            "is_public",
            "created_at",
        )
        read_only_fields = ("id", "created_at")

    def validate(self, attrs):
        instance = self.instance or Habit()
        for field, value in attrs.items():
            setattr(instance, field, value)
        if not self.instance:
            instance.user = self.context["request"].user
        validate_habit_fields(instance)
        return attrs

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class PublicHabitSerializer(serializers.ModelSerializer):
    """Сериализатор публичных привычек (только чтение)."""

    user = serializers.StringRelatedField()

    class Meta:
        model = Habit
        fields = (
            "id",
            "user",
            "place",
            "time",
            "action",
            "periodicity",
            "execution_time",
            "created_at",
        )
        read_only_fields = fields
