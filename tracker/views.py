from django.db.models import Count, Prefetch, Q
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from tracker.models import Employee, Task
from tracker.serializers import BusyEmployeeSerializer, EmployeeSerializer, TaskSerializer


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = (AllowAny,)
    pagination_class = None

    @extend_schema(
        summary="Занятые сотрудники",
        description=(
            "Сотрудники и их задачи, отсортированные по количеству активных задач "
            "(статусы: new, in_progress, blocked)."
        ),
        responses=BusyEmployeeSerializer(many=True),
    )
    @action(detail=False, methods=["get"], url_path="busy")
    def busy(self, request):
        active_filter = Q(tasks__status__in=Task.active_statuses())
        queryset = (
            Employee.objects.annotate(active_tasks_count=Count("tasks", filter=active_filter))
            .prefetch_related(Prefetch("tasks", queryset=Task.objects.order_by("id")))
            .order_by("-active_tasks_count", "id")
        )
        serializer = BusyEmployeeSerializer(queryset, many=True)
        return Response(serializer.data)


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.select_related("parent", "assignee").all()
    serializer_class = TaskSerializer
    permission_classes = (AllowAny,)
    pagination_class = None

    @extend_schema(
        summary="Важные задачи",
        description=(
            "Задачи со статусом new и без исполнителя, от которых зависят задачи "
            "в статусах in_progress или blocked."
        ),
    )
    @action(detail=False, methods=["get"], url_path="important")
    def important(self, request):
        employee_load = {
            row["id"]: row["active_tasks_count"]
            for row in Employee.objects.annotate(
                active_tasks_count=Count(
                    "tasks", filter=Q(tasks__status__in=Task.active_statuses())
                )
            ).values("id", "active_tasks_count")
        }

        least_loaded_employee = (
            Employee.objects.annotate(
                active_tasks_count=Count(
                    "tasks", filter=Q(tasks__status__in=Task.active_statuses())
                )
            )
            .order_by("active_tasks_count", "id")
            .first()
        )

        least_loaded_count = (
            least_loaded_employee.active_tasks_count if least_loaded_employee else None
        )

        important_tasks = (
            Task.objects.filter(
                assignee__isnull=True,
                status=Task.Status.NEW,
                subtasks__status__in=Task.in_work_statuses(),
            )
            .distinct()
            .select_related("parent", "parent__assignee")
            .order_by("deadline", "id")
        )

        data = []
        for task in important_tasks:
            candidates = []
            if least_loaded_employee:
                candidates.append(least_loaded_employee.full_name)

            parent_assignee = task.parent.assignee if task.parent else None
            if parent_assignee and least_loaded_count is not None:
                parent_load = employee_load.get(parent_assignee.id, 0)
                if parent_load <= least_loaded_count + 2:
                    candidates.append(parent_assignee.full_name)

            data.append(
                {
                    "важная_задача": task.title,
                    "срок": task.deadline,
                    "ФИО_сотрудника": sorted(set(candidates)),
                }
            )

        return Response(data)
