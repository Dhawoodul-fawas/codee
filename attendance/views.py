from rest_framework.views import APIView
from django.utils import timezone
from apk.models import Attendance, Leave
from apk.serializers import AttendanceSerializer, LeaveSerializer
from employees.models import Employee
from apk.utils import api_response  

class AdminAttendanceList(APIView):
    def get(self, request):
        user_type = request.GET.get("type")  

        # 1️⃣ Filter employees
        employees = Employee.objects.all()
        if user_type == "employee":
            employees = employees.filter(employee_id__startswith="EMP")
        elif user_type == "intern":
            employees = employees.filter(employee_id__startswith="INT")

        employee_ids = employees.values_list("id", flat=True)

        attendance = Attendance.objects.filter(employee_id__in=employee_ids)
        leaves = Leave.objects.filter(employee_id__in=employee_ids)

        attendance_data = AttendanceSerializer(attendance, many=True).data
        leave_data = LeaveSerializer(leaves, many=True).data

        formatted_leaves = []
        for leave in leave_data:
            formatted_leaves.append({
                "id": leave["id"],
                "employee_id": leave["employee_id"],
                "employee_name": leave["employee_name"],
                "date": leave["leave_date"],
                "check_in": None,
                "check_out": None,
                "working_hours": None,
                "overtime_hours": None,
                "reason": leave["reason"],
            })

        for a in attendance_data:
            a["reason"] = None
        
        combined = attendance_data + formatted_leaves
        combined_sorted = sorted(combined, key=lambda x: x["date"], reverse=True)

        return api_response(
            True,
            "Attendance fetched successfully",
            combined_sorted
        )
