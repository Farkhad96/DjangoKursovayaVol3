from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from habits.models import Habit
from habits.pagination import HabitPagination
from habits.permissions import IsOwnerOrReadOnlyPublic
from habits.serializers import HabitSerializer, PublicHabitSerializer


@extend_schema_view(
    list=extend_schema(summary="Список привычек текущего пользователя"),
    create=extend_schema(summary="Создание привычки"),
    retrieve=extend_schema(summary="Получение привычки"),
    update=extend_schema(summary="Обновление привычки"),
    partial_update=extend_schema(summary="Частичное обновление привычки"),
    destroy=extend_schema(summary="Удаление привычки"),
)
class HabitViewSet(viewsets.ModelViewSet):
    """CRUD для привычек текущего пользователя."""

    serializer_class = HabitSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnlyPublic)
    pagination_class = HabitPagination

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)


@extend_schema(summary="Список публичных привычек")
class PublicHabitListView(generics.ListAPIView):
    """Список публичных привычек (только чтение)."""

    queryset = Habit.objects.filter(is_public=True)
    serializer_class = PublicHabitSerializer
    permission_classes = (AllowAny,)
    pagination_class = HabitPagination
