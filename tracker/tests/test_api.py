from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from tracker.models import Employee, Task


class EmployeeTaskApiTests(APITestCase):
    def test_employee_crud(self):
        create_response = self.client.post(
            reverse("employee-list"),
            {"full_name": "Иван Иванов", "position": "Разработчик"},
            format="json",
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        employee_id = create_response.data["id"]
        detail_url = reverse("employee-detail", kwargs={"pk": employee_id})

        patch_response = self.client.patch(
            detail_url,
            {"position": "Старший разработчик"},
            format="json",
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)

        list_response = self.client.get(reverse("employee-list"))
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_response.data), 1)

        delete_response = self.client.delete(detail_url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

    def test_task_crud(self):
        employee = Employee.objects.create(full_name="Иван Иванов", position="QA")

        create_response = self.client.post(
            reverse("task-list"),
            {
                "title": "Подготовить отчет",
                "assignee": employee.id,
                "deadline": (timezone.now() + timedelta(days=1)).isoformat(),
                "status": Task.Status.NEW,
            },
            format="json",
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        task_id = create_response.data["id"]
        detail_url = reverse("task-detail", kwargs={"pk": task_id})

        patch_response = self.client.patch(
            detail_url,
            {"status": Task.Status.IN_PROGRESS},
            format="json",
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)

        delete_response = self.client.delete(detail_url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

    def test_task_cannot_reference_itself_as_parent(self):
        task = Task.objects.create(
            title="Задача",
            deadline=timezone.now() + timedelta(days=1),
            status=Task.Status.NEW,
        )

        response = self.client.patch(
            reverse("task-detail", kwargs={"pk": task.id}),
            {"parent": task.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent", response.data)


class SpecialEndpointsTests(APITestCase):
    def test_busy_employees_sorted_by_active_tasks_count(self):
        first = Employee.objects.create(full_name="Алексей", position="Backend")
        second = Employee.objects.create(full_name="Мария", position="Frontend")

        now = timezone.now()
        Task.objects.create(
            title="Task 1",
            assignee=first,
            deadline=now + timedelta(days=1),
            status=Task.Status.NEW,
        )
        Task.objects.create(
            title="Task 2",
            assignee=first,
            deadline=now + timedelta(days=1),
            status=Task.Status.IN_PROGRESS,
        )
        Task.objects.create(
            title="Task 3",
            assignee=second,
            deadline=now + timedelta(days=1),
            status=Task.Status.DONE,
        )

        response = self.client.get(reverse("employee-busy"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], first.id)
        self.assertEqual(response.data[0]["active_tasks_count"], 2)
        self.assertEqual(response.data[1]["active_tasks_count"], 0)

    def test_important_tasks_candidate_selection_with_edge_case(self):
        least = Employee.objects.create(full_name="Least Loaded", position="PM")
        zero_load = Employee.objects.create(full_name="Zero Load", position="Analyst")
        parent_assignee = Employee.objects.create(
            full_name="Parent Assignee", position="Lead"
        )
        excluded_assignee = Employee.objects.create(
            full_name="Excluded Assignee", position="Lead"
        )

        now = timezone.now()

        Task.objects.create(
            title="least task",
            assignee=least,
            deadline=now + timedelta(days=1),
            status=Task.Status.NEW,
        )

        parent_for_include = Task.objects.create(
            title="Parent Include",
            assignee=parent_assignee,
            deadline=now + timedelta(days=2),
            status=Task.Status.IN_PROGRESS,
        )
        for i in range(1):
            Task.objects.create(
                title=f"parent include load {i}",
                assignee=parent_assignee,
                deadline=now + timedelta(days=2),
                status=Task.Status.NEW,
            )

        parent_for_exclude = Task.objects.create(
            title="Parent Exclude",
            assignee=excluded_assignee,
            deadline=now + timedelta(days=2),
            status=Task.Status.IN_PROGRESS,
        )
        for i in range(4):
            Task.objects.create(
                title=f"parent exclude load {i}",
                assignee=excluded_assignee,
                deadline=now + timedelta(days=2),
                status=Task.Status.NEW,
            )

        important_include = Task.objects.create(
            title="Important Include",
            parent=parent_for_include,
            deadline=now + timedelta(hours=6),
            status=Task.Status.NEW,
            assignee=None,
        )
        Task.objects.create(
            title="Dependent in progress",
            parent=important_include,
            deadline=now + timedelta(hours=7),
            status=Task.Status.IN_PROGRESS,
            assignee=least,
        )

        important_exclude = Task.objects.create(
            title="Important Exclude",
            parent=parent_for_exclude,
            deadline=now + timedelta(hours=8),
            status=Task.Status.NEW,
            assignee=None,
        )
        Task.objects.create(
            title="Dependent blocked",
            parent=important_exclude,
            deadline=now + timedelta(hours=9),
            status=Task.Status.BLOCKED,
            assignee=least,
        )

        response = self.client.get(reverse("task-important"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([item["важная_задача"] for item in response.data], [
            "Important Include",
            "Important Exclude",
        ])
        self.assertEqual(
            response.data[0]["ФИО_сотрудника"],
            ["Parent Assignee", "Zero Load"],
        )
        self.assertEqual(response.data[1]["ФИО_сотрудника"], ["Zero Load"])
