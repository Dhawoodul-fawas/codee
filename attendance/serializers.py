# attendance/serializers.py
from rest_framework import serializers
from .models import Attendance

class AttendanceSerializer(serializers.ModelSerializer):
    employee_id = serializers.CharField(source="employee.employee_id", read_only=True)
    name = serializers.CharField(source="employee.name", read_only=True)
    department = serializers.CharField(source="employee.department", read_only=True)

    working_hours = serializers.DurationField(read_only=True)
    overtime = serializers.DurationField(read_only=True)

    class Meta:
        model = Attendance
        fields = [
            "id",
            "employee",
            "employee_id",
            "name",
            "department",
            "date",
            "checkin",
            "checkout",
            "break_time",
            "working_hours",
            "overtime",
            "on_leave",
        ]
