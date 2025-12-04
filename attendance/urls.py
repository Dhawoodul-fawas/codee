from django.urls import path
from .views import (
    AttendanceViewSet,
    AttendanceAllListView,
    EmployeeAttendanceListView,
    InternAttendanceListView
)

attendance_create = AttendanceViewSet.as_view({
    "post": "create"       
})

attendance_detail = AttendanceViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy"
})

urlpatterns = [
    # main list + create
    path("attendance-create/", attendance_create, name="attendance-create"),
    path("attendance-edit/<int:pk>/", attendance_detail, name="attendance-detail"),

    # separate lists
    path("attendance/all/", AttendanceAllListView.as_view(), name="attendance-all"),
    path("attendance/employees/", EmployeeAttendanceListView.as_view(), name="attendance-employees"),
    path("attendance/interns/", InternAttendanceListView.as_view(), name="attendance-interns"),
]
