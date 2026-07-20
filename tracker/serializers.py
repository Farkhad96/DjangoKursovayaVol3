from rest_framework import serializers

from tracker.models import Employee, Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "parent",
            "assignee",
            "deadline",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        parent = attrs.get("parent")
        instance = getattr(self, "instance", None)

        if instance and parent and parent.pk == instance.pk:
            raise serializers.ValidationError(
                {"parent": "Задача не может быть родителем самой себя."}
            )

        return attrs


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ["id", "full_name", "position", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class EmployeeTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["id", "title", "deadline", "status", "parent", "assignee"]


class BusyEmployeeSerializer(serializers.ModelSerializer):
    tasks = EmployeeTaskSerializer(many=True, read_only=True)
    active_tasks_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Employee
        fields = ["id", "full_name", "position", "active_tasks_count", "tasks"]
