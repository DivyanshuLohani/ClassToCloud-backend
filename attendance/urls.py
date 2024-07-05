from django.urls import path
from .views import AddAttendance

urlpatterns = (
    path("", AddAttendance.as_view(), name="add_attendance"),
    path("list/", AddAttendance.as_view(), name="add_attendance_bulk"),
)
