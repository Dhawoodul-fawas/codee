from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
from django.db.models.functions import TruncMonth
from datetime import date

from employees.models import Employee
from project.models import PhaseTask, Project
from apk.models import Attendance


# ---------------------------------------------
# Project status from Phase → Task
# ---------------------------------------------
def get_project_status(project):
    tasks = PhaseTask.objects.filter(phase__project=project)

    if not tasks.exists():
        return "pending"

    if not tasks.exclude(status="completed").exists():
        return "completed"

    return "ongoing"


# ---------------------------------------------
# TOP DASHBOARD CARDS
# ---------------------------------------------
class DashboardSummaryAPIView(APIView):
    def get(self, request):

        active_employees = Employee.objects.filter(
            employee_id__startswith="EMP",
            status="active"
        ).count()

        active_interns = Employee.objects.filter(
            employee_id__startswith="INT",
            status="active"
        ).count()

        project_count = Project.objects.count()

        total_staff = Employee.objects.filter(
            employee_id__startswith="EMP",
            status="active"
        ).count()

        present_today = Attendance.objects.filter(
            date=date.today(),
            employee__employee_id__startswith="EMP"
        ).values("employee").distinct().count()

        attendance_percent = (
            (present_today / total_staff) * 100 if total_staff else 0
        )

        return Response({
            "success": True,
            "active_employees": active_employees,
            "active_interns": active_interns,
            "project_count": project_count,
            "attendance_percent": round(attendance_percent, 1)
        })


# ---------------------------------------------
# ONGOING PROJECT LIST
# ---------------------------------------------
class OngoingProjectsAPIView(APIView):
    def get(self, request):

        projects = Project.objects.prefetch_related(
            "phases__tasks", "team_members"
        )

        data = []

        for p in projects:
            if get_project_status(p) != "ongoing":
                continue

            total_tasks = PhaseTask.objects.filter(
                phase__project=p
            ).count()

            completed_tasks = PhaseTask.objects.filter(
                phase__project=p,
                status="completed"
            ).count()

            progress = int((completed_tasks / total_tasks) * 100) if total_tasks else 0

            members = [
                m.profile_image.url if m.profile_image else ""
                for m in p.team_members.all()
            ]

            data.append({
                "name": p.project_name,
                "description": p.description,
                "progress": progress,
                "due_date": p.end_date,
                "logo": p.project_logo.url if p.project_logo else "",
                "members": members
            })

        return Response({"success": True, "data": data[:10]})


# ---------------------------------------------
# BAR GRAPH (Monthly Attendance)
# ---------------------------------------------
class PerformanceGraphAPIView(APIView):
    def get(self, request):

        qs = Attendance.objects.filter(
            employee__employee_id__startswith="EMP"
        ).annotate(
            month=TruncMonth("date")
        ).values("month").annotate(
            total=Count("id")
        ).order_by("month")

        months = []
        values = []

        for row in qs:
            months.append(row["month"].strftime("%b"))
            values.append(row["total"])

        return Response({
            "success": True,
            "months": months,
            "values": values
        })


# ---------------------------------------------
# DONUT CHART (Project Status)
# ---------------------------------------------
class ProjectStatusAPIView(APIView):
    def get(self, request):

        completed = 0
        ongoing = 0
        pending = 0

        for project in Project.objects.prefetch_related("phases__tasks"):
            status = get_project_status(project)

            if status == "completed":
                completed += 1
            elif status == "ongoing":
                ongoing += 1
            else:
                pending += 1

        return Response({
            "success": True,
            "data": {
                "completed": completed,
                "ongoing": ongoing,
                "pending": pending
            }
        })
