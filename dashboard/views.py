from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
from django.db.models.functions import TruncMonth
from datetime import date
from rest_framework.permissions import AllowAny
from dashboard.utils import api_response
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
    permission_classes = [AllowAny]

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

        total_staff = active_employees

        present_today = Attendance.objects.filter(
            date=date.today(),
            employee__employee_id__startswith="EMP"
        ).values("employee").distinct().count()

        attendance_percent = (
            (present_today / total_staff) * 100 if total_staff else 0
        )

        return api_response(
            success=True,
            message="Dashboard summary fetched successfully",
            data={
                "active_employees": active_employees,
                "active_interns": active_interns,
                "project_count": project_count,
                "attendance_percent": round(attendance_percent, 1)
            }
        )


# ---------------------------------------------
# ONGOING PROJECT LIST
# ---------------------------------------------
class OngoingProjectsAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):

        projects = Project.objects.prefetch_related(
            "phases__tasks", "team_members"
        )

        data = []

        for p in projects:
            if get_project_status(p) != "ongoing":
                continue

            tasks = PhaseTask.objects.filter(phase__project=p)

            total_tasks = tasks.count()
            completed_tasks = tasks.filter(status="completed").count()

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

        return api_response(
            success=True,
            message="Ongoing projects fetched successfully",
            data=data[:10]
        )



# ---------------------------------------------
# BAR GRAPH (Monthly Attendance)
# ---------------------------------------------
class PerformanceGraphAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):

        qs = Attendance.objects.filter(
            employee__employee_id__startswith="EMP"
        ).annotate(
            month=TruncMonth("date")
        ).values("month").annotate(
            total=Count("id")
        ).order_by("month")

        months = [row["month"].strftime("%b") for row in qs]
        values = [row["total"] for row in qs]

        return api_response(
            success=True,
            message="Attendance performance graph data fetched",
            data={
                "months": months,
                "values": values
            }
        )



# ---------------------------------------------
# DONUT CHART (Project Status)
# ---------------------------------------------
class ProjectStatusAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):

        completed = ongoing = pending = 0

        projects = Project.objects.prefetch_related("phases__tasks")
        total_projects = projects.count()

        if total_projects == 0:
            return api_response(
                success=True,
                message="Project status fetched successfully",
                data={
                    "completed": 0,
                    "ongoing": 0,
                    "pending": 0
                }
            )

        for project in projects:
            status = get_project_status(project)

            if status == "completed":
                completed += 1
            elif status == "ongoing":
                ongoing += 1
            else:
                pending += 1

        return api_response(
            success=True,
            message="Project status fetched successfully",
            data={
                "completed": round((completed / total_projects) * 100, 2),
                "ongoing": round((ongoing / total_projects) * 100, 2),
                "pending": round((pending / total_projects) * 100, 2)
            }
        )
