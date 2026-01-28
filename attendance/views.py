from rest_framework.views import APIView
from django.utils import timezone
from apk.models import Attendance, Leave
from apk.serializers import AttendanceSerializer, LeaveSerializer
from employees.models import Employee
from apk.utils import api_response  
from rest_framework.permissions import AllowAny

class AdminAttendanceList(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        user_type = request.GET.get("type")  # employee | intern | None

        # 1️⃣ Filter employees
        employees = Employee.objects.all()

        if user_type == "employee":
            employees = employees.filter(employee_id__startswith="EMP")
        elif user_type == "intern":
            employees = employees.filter(employee_id__startswith="INT")

        # 2️⃣ Attendance & Leave
        attendance = Attendance.objects.filter(
            employee__in=employees
        )

        leaves = Leave.objects.filter(
            employee__in=employees
        )

        attendance_data = AttendanceSerializer(
            attendance,
            many=True,
            context={"request": request}
        ).data

        leave_data = LeaveSerializer(
            leaves,
            many=True,
            context={"request": request}
        ).data

        # 3️⃣ Normalize leave records to attendance format
        formatted_leaves = [
            {
                "id": leave["id"],
                "employee_id": leave["employee_id"],
                "employee_name": leave["employee_name"],
                "date": leave["leave_date"],
                "check_in": None,
                "check_out": None,
                "working_hours": None,
                "overtime_hours": None,
                "reason": leave["reason"],
            }
            for leave in leave_data
        ]

        # 4️⃣ Ensure attendance also has `reason`
        for a in attendance_data:
            a["reason"] = None

        # 5️⃣ Merge & sort
        combined = attendance_data + formatted_leaves
        combined_sorted = sorted(
            combined,
            key=lambda x: x["date"],
            reverse=True
        )

        return api_response(
            success=True,
            message="Attendance fetched successfully",
            data=combined_sorted
        )
