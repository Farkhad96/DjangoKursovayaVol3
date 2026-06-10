from django.core.exceptions import ValidationError


def validate_execution_time(value):
    """Время выполнения не должно превышать 120 секунд."""
    if value > 120:
        raise ValidationError(
            "Время на выполнение привычки не может превышать 120 секунд."
        )


def validate_periodicity(value):
    """Периодичность от 1 до 7 дней."""
    if value < 1 or value > 7:
        raise ValidationError(
            "Периодичность должна быть от 1 до 7 дней "
            "(не реже 1 раза в неделю и не чаще ежедневно)."
        )


def validate_habit_fields(instance):
    """Комплексная валидация полей привычки."""
    if instance.related_habit and instance.reward:
        raise ValidationError(
            "Нельзя одновременно указывать связанную привычку и вознаграждение."
        )

    if instance.is_pleasant:
        if instance.reward:
            raise ValidationError(
                "У приятной привычки не может быть вознаграждения."
            )
        if instance.related_habit:
            raise ValidationError(
                "У приятной привычки не может быть связанной привычки."
            )

    if instance.related_habit and not instance.related_habit.is_pleasant:
        raise ValidationError(
            "В связанные привычки могут попадать только приятные привычки."
        )

    if instance.related_habit and instance.related_habit.user != instance.user:
        raise ValidationError(
            "Связанная привычка должна принадлежать тому же пользователю."
        )
