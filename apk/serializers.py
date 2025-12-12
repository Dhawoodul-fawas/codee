from rest_framework import serializers
from employees.models import Employee
from .models import Attendance, Leave, LoginHistory


class AttendanceSerializer(serializers.ModelSerializer):
    # OUTPUT employee_id
    employee_id = serializers.CharField(source="employee.employee_id", read_only=True)

    # OUTPUT employee_name
    employee_name = serializers.CharField(source="employee.name", read_only=True)

    # INPUT employee_id
    input_employee_id = serializers.CharField(write_only=True)

    class Meta:
        model = Attendance
        fields = [
            'id',
            'employee_id',        # output
            'input_employee_id',  # input
            'employee_name',
            'date',
            'check_in',
            'check_out',
            'working_hours',
            'overtime_hours',
        ]
        read_only_fields = ['working_hours', 'overtime_hours', 'employee_name', 'employee_id']

    def validate(self, data):
        emp_id = data.get("input_employee_id")
        date = data.get("date")

        # Validate employee exists
        try:
            employee = Employee.objects.get(employee_id=emp_id)
        except Employee.DoesNotExist:
            raise serializers.ValidationError({"detail": "Invalid employee_id"})

        data["employee"] = employee

        # Check duplicate attendance
        existing = Attendance.objects.filter(employee=employee, date=date)

        if self.instance:
            existing = existing.exclude(id=self.instance.id)

        if existing.exists():
            raise serializers.ValidationError(
                {"detail": "Attendance already exists for this employee on this date."}
            )

        return data

    def create(self, validated_data):
        validated_data.pop("input_employee_id")
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop("input_employee_id", None)
        return super().update(instance, validated_data)




class LeaveSerializer(serializers.ModelSerializer):
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    employee_name = serializers.CharField(source="employee.name", read_only=True)

    class Meta:
        model = Leave
        fields = [
            'id',
            'employee_id',
            'employee_name',
            'leave_date',
            'reason'
        ]


class LoginHistorySerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)

    class Meta:
        model = LoginHistory
        fields = [
            'id',
            'employee_name',
            'employee_id',
            'login_time',
            'login_date',
        ]
