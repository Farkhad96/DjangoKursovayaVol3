from django.db import models


class Employee(models.Model):
    full_name = models.CharField(max_length=255, verbose_name="ФИО")
    position = models.CharField(max_length=255, verbose_name="Должность")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"

    def __str__(self):
        return self.full_name


class Task(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Новая"
        IN_PROGRESS = "in_progress", "В работе"
        BLOCKED = "blocked", "Заблокирована"
        DONE = "done", "Завершена"
        CANCELED = "canceled", "Отменена"

    title = models.CharField(max_length=255, verbose_name="Наименование")
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subtasks",
        verbose_name="Родительская задача",
    )
    assignee = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
        verbose_name="Исполнитель",
    )
    deadline = models.DateTimeField(verbose_name="Срок")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        verbose_name="Статус",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        indexes = [models.Index(fields=["status"]), models.Index(fields=["deadline"])]

    @classmethod
    def active_statuses(cls):
        return [cls.Status.NEW, cls.Status.IN_PROGRESS, cls.Status.BLOCKED]

    @classmethod
    def in_work_statuses(cls):
        return [cls.Status.IN_PROGRESS, cls.Status.BLOCKED]

    def __str__(self):
        return self.title
