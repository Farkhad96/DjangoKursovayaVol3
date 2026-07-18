from django.urls import include, path
from rest_framework.routers import DefaultRouter

from tracker.views import EmployeeViewSet, TaskViewSet

router = DefaultRouter()
router.register("employees", EmployeeViewSet, basename="employee")
router.register("tasks", TaskViewSet, basename="task")

urlpatterns = [
    path("", include(router.urls)),
]
