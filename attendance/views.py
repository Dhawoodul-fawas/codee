from rest_framework import generics, viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Attendance
from .serializers import AttendanceSerializer
from .filters import AttendanceFilter


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.select_related("employee").all().order_by("-date")
    serializer_class = AttendanceSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = AttendanceFilter
    search_fields = ["employee__employee_id", "employee__name"]



class AttendanceAllListView(generics.ListAPIView):
    queryset = Attendance.objects.select_related("employee").all().order_by("-date")
    serializer_class = AttendanceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["employee__employee_id", "employee__name"]


class EmployeeAttendanceListView(generics.ListAPIView):
    serializer_class = AttendanceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["employee__employee_id", "employee__name"]

    def get_queryset(self):
        return Attendance.objects.filter(
            employee__role="staff"
        ).select_related("employee").order_by("-date")


class InternAttendanceListView(generics.ListAPIView):
    serializer_class = AttendanceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["employee__employee_id", "employee__name"]

    def get_queryset(self):
        return Attendance.objects.filter(
            employee__role="intern"
        ).select_related("employee").order_by("-date")
