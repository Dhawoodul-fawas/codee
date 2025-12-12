from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import date
from django.db.models import Count
# adjust imports to your apps
from employees.models import Employee
from project.models import Project
from apk.models import Attendance
from apk.models import Leave


class DashboardSummaryAPIView(APIView):
    def get(self, request):

        # Active employees having EMP ID
        active_employees = Employee.objects.filter(
            employee_id__startswith="EMP",
            status="active"
        ).count()

        # Active interns
        active_interns = Employee.objects.filter(
            employee_id__startswith="INT",
            status="active"
        ).count()

        # Total projects
        total_projects = Project.objects.count()

        # Attendance % Calculation
        total_staff = Employee.objects.filter(status="active").count()
        present_today = Attendance.objects.filter(
            date=date.today()
        ).values("employee").distinct().count()

        attendance_percent = (
            present_today / total_staff * 100 if total_staff > 0 else 0
        )

        return Response({
            "success": True,
            "active_employees": active_employees,
            "active_interns": active_interns,
            "project_count": total_projects,
            "attendance_percent": round(attendance_percent, 1)
        })


class OngoingProjectsAPIView(APIView):
    def get(self, request):

        projects = Project.objects.filter(
            project_status__iexact="ongoing"
        ).order_by("-id")[:10]

        data = []

        for p in projects:
            members = []
            if hasattr(p, "project_team"):
                members = [
                    (m.profile_image.url if m.profile_image else "")
                    for m in p.project_team.all()
                ]

            data.append({
                "name": p.project_name,
                "description": getattr(p, "description", ""),
                "progress": getattr(p, "progress", 0),
                "due_date": p.due_date,
                "logo": p.project_logo.url if p.project_logo else "",
                "members": members
            })

        return Response({"success": True, "data": data})




class PerformanceGraphAPIView(APIView):
    def get(self, request):
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"]
        values = [40, 60, 35, 80, 45, 50, 70]

        return Response({
            "success": True,
            "months": months,
            "values": values
        })



class ProjectStatusAPIView(APIView):
    def get(self, request):

        completed = Project.objects.filter(
            project_status__iexact="completed"
        ).count()

        ongoing = Project.objects.filter(
            project_status__iexact="ongoing"
        ).count()

        pending = Project.objects.filter(
            project_status__iexact="pending"
        ).count()

        return Response({
            "success": True,
            "data": {
                "completed": completed,
                "ongoing": ongoing,
                "pending": pending
            }
        })




