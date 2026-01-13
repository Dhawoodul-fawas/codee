from datetime import date
import re
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework import status
from django.contrib.auth.hashers import check_password
from .models import Attendance, Leave, LoginHistory
from .serializers import AttendanceSerializer, LeaveSerializer, LoginHistorySerializer
from employees.models import Employee
from rest_framework.generics import ListAPIView
from .utils import api_response 
from .utils import api_response, create_employee_token


class ApkLoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return api_response(False, "Email and password required", None, 400)

        # Gmail-only validation
        pattern = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'
        if not re.match(pattern, email):
            return api_response(False, "Only gmail.com email is allowed", None, 400)

        try:
            user = Employee.objects.get(email__iexact=email)
        except Employee.DoesNotExist:
            return api_response(False, "Invalid credentials", None, 400)

        # ✅ Only hash check — DO NOT re-validate format
        if not check_password(password, user.password):
            return api_response(False, "Invalid credentials", None, 400)

        today = date.today()

        if not LoginHistory.objects.filter(employee=user, login_date=today).exists():
            LoginHistory.objects.create(employee=user)

        token = create_employee_token(user)

        return api_response(
            True,
            "Login Successful",
            {
                "employee_id": user.employee_id,
                "name": user.name,
                "role": user.role,
                "department": user.department,
                "access_token": token
            }
        )


# ✅ CHECK-IN / CHECK-OUT (FIXED & SAFE)
class CheckInOutView(APIView):
    def post(self, request):
        employee_code = request.data.get("employee")

        try:
            employee = Employee.objects.get(employee_id=employee_code)
        except Employee.DoesNotExist:
            return api_response(False, "Invalid Employee", None, 400)

        now = timezone.now()
        today = date.today()

        # 🔍 Find last open session (check_in but no check_out)
        last_session = Attendance.objects.filter(
            employee=employee,
            check_out__isnull=True
        ).order_by('-check_in').first()

        # 1️⃣ If NO open session → create NEW check-in
        if not last_session:
            Attendance.objects.create(
                employee=employee,
                date=today,        # IMPORTANT
                check_in=now
            )
            return api_response(True, "Checked in successfully", {
                "status": "CHECKED_IN",
                "time": now,
            })

        # 2️⃣ If there is an open session → CHECK OUT
        last_session.check_out = now
        last_session.save()

        return api_response(True, "Checked out successfully", {
            "status": "CHECKED_OUT",
            "time": now,
        })



# ✅ APPLY LEAVE (FIXED)
class ApplyLeaveView(APIView):
    def post(self, request):
        employee_code = request.data.get("employee")
        leave_date = request.data.get("leave_date")
        reason = request.data.get("reason")

        # Validate inputs
        if not employee_code:
            return api_response(False, "Employee code is required", None, 400)

        if not leave_date:
            return api_response(False, "Leave date is required", None, 400)

        if not reason:
            return api_response(False, "Reason is required", None, 400)

        # Check employee exists
        try:
            employee = Employee.objects.get(employee_id=employee_code)
        except Employee.DoesNotExist:
            return api_response(False, "Invalid Employee", None, 400)

        # ❌ Prevent duplicate leave
        if Leave.objects.filter(employee=employee, leave_date=leave_date).exists():
            return api_response(False, "Leave already applied for this date", None, 400)

        # Create leave
        leave = Leave.objects.create(
            employee=employee,
            leave_date=leave_date,
            reason=reason
        )

        return api_response(True, "Leave applied successfully", LeaveSerializer(leave).data)



# ✅ HOME PAGE STATUS (SHOW TODAY CHECK-IN & CHECK-OUT)
class HomeAttendanceStatusView(APIView):
    def post(self, request):
        employee_code = request.data.get("employee")

        try:
            employee = Employee.objects.get(employee_id=employee_code)
        except Employee.DoesNotExist:
            return api_response(False, "Invalid Employee", None, 400)

        today = date.today()

        last_session = Attendance.objects.filter(
            employee=employee,
            check_in__date=today
        ).order_by('-check_in').first()

        if not last_session:
            return api_response(True, "No attendance marked today", {
                "date": str(today),
                "check_in": None,
                "check_out": None
            })

        return api_response(True, "Attendance status fetched", {
            "date": str(today),
            "check_in": last_session.check_in,
            "check_out": last_session.check_out
        })

class LeaveListView(APIView):
    def get(self, request):
        employee_code = request.query_params.get("employee") 

        # If filtering by employee
        if employee_code:
            try:
                employee = Employee.objects.get(employee_id=employee_code)
            except Employee.DoesNotExist:
                return api_response(False, "Invalid Employee ID", None, 400)

            leaves = Leave.objects.filter(employee=employee).order_by("-leave_date")
        else:
            # Return all leaves
            leaves = Leave.objects.all().order_by("-leave_date")

        serializer = LeaveSerializer(leaves, many=True)
        return api_response(True, "Leave list fetched successfully", serializer.data)


class AttendanceListView(APIView):
    def get(self, request):
        user_type = request.GET.get("type")  # employee / intern / None

        # 1️⃣ Filter employees
        employees = Employee.objects.all()
        if user_type == "employee":
            employees = employees.filter(employee_id__startswith="EMP")
        elif user_type == "intern":
            employees = employees.filter(employee_id__startswith="INT")

        employee_ids = employees.values_list("id", flat=True)

        # 2️⃣ Fetch attendance + leave
        attendance = Attendance.objects.filter(employee_id__in=employee_ids)
        leaves = Leave.objects.filter(employee_id__in=employee_ids)

        # 3️⃣ Serialize
        attendance_data = AttendanceSerializer(attendance, many=True).data
        leave_data = LeaveSerializer(leaves, many=True).data

        # 4️⃣ Format LEAVE records (KEEP reason, remove status)
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
                "reason": leave["reason"]      # Only for leave
            })

        # 5️⃣ Format attendance records (remove status + keep reason None)
        for a in attendance_data:
            a["reason"] = None                # present has no reason
            if "status" in a:
                a.pop("status")

        # 6️⃣ Merge
        combined = attendance_data + formatted_leaves

        # 7️⃣ Sort by date
        combined_sorted = sorted(combined, key=lambda x: x["date"], reverse=True)

        return api_response(
            True,
            "Attendance + Leave list fetched successfully",
            combined_sorted
        )


class LoginListView(ListAPIView):
    queryset = LoginHistory.objects.all().order_by('-login_time')
    serializer_class = LoginHistorySerializer

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        return api_response(
            True,
            "Login history fetched successfully",
            response.data
        )
class LogoutView(APIView):
    def post(self, request):
        emp_code = request.data.get("employee_id")

        if not emp_code:
            return api_response(False, "employee_id is required", status=400)

        try:
            # Find employee by code
            employee = Employee.objects.get(employee_id=emp_code)

            # Find today’s login record
            login_record = LoginHistory.objects.filter(
                employee=employee,
                login_date=timezone.now().date()
            ).first()

            if not login_record:
                return api_response(False, "No login found for today", status=400)

            # Update logout time
            login_record.logout_time = timezone.now()
            login_record.save()

            return api_response(True, "Logout successful", {
                "employee_id": emp_code,
                "logout_time": login_record.logout_time
            })

        except Employee.DoesNotExist:
            return api_response(False, "Employee not found", status=404)