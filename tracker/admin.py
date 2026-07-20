from django.contrib import admin

from tracker.models import Employee, Task


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "position", "created_at")
    search_fields = ("full_name", "position")


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "status", "assignee", "deadline", "parent")
    list_filter = ("status",)
    search_fields = ("title",)
