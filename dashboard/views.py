from datetime import date

from django.db.models import (
    Count, Q, Case, When, Value, CharField,F
)
from django.db.models.functions import TruncMonth

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from dashboard.utils import api_response
from employees.models import Employee
from project.models import Project
from apk.models import Attendance


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

        present_today = Attendance.objects.filter(
            date=date.today(),
            employee__employee_id__startswith="EMP"
        ).values("employee").distinct().count()

        attendance_percent = round(
            (present_today / active_employees) * 100, 1
        ) if active_employees else 0

        return api_response(
            success=True,
            message="Dashboard summary fetched successfully",
            data={
                "active_employees": active_employees,
                "active_interns": active_interns,
                "project_count": project_count,
                "attendance_percent": attendance_percent
            }
        )


# ---------------------------------------------
# ONGOING PROJECT LIST (Optimized)
# ---------------------------------------------
class OngoingProjectsAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):

        projects = (
            Project.objects
            .annotate(
                total_tasks=Count("phases__tasks", distinct=True),
                completed_tasks=Count(
                    "phases__tasks",
                    filter=Q(phases__tasks__status="completed"),
                    distinct=True
                ),
            )
            .annotate(
                computed_status=Case(
                    When(total_tasks=0, then=Value("pending")),
                    When(total_tasks=F("completed_tasks"), then=Value("completed")),
                    default=Value("ongoing"),
                    output_field=CharField(),
                )
            )
            .filter(computed_status="ongoing")
            .prefetch_related("team_members")[:10]
        )

        data = []

        for p in projects:
            progress = int(
                (p.completed_tasks / p.total_tasks) * 100
            ) if p.total_tasks else 0

            data.append({
                "name": p.project_name,
                "description": p.description,
                "progress": progress,
                "due_date": p.end_date,
                "logo": p.project_logo.url if p.project_logo else "",
                "members": [
                    m.profile_image.url if m.profile_image else ""
                    for m in p.team_members.all()
                ]
            })

        return api_response(
            success=True,
            message="Ongoing projects fetched successfully",
            data=data
        )

# ---------------------------------------------
# BAR GRAPH (Monthly Attendance)
# ---------------------------------------------
class PerformanceGraphAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):

        qs = (
            Attendance.objects
            .filter(employee__employee_id__startswith="EMP")
            .annotate(month=TruncMonth("date"))
            .values("month")
            .annotate(total=Count("id"))
            .order_by("month")
        )

        return api_response(
            success=True,
            message="Attendance performance graph data fetched",
            data={
                "months": [row["month"].strftime("%b") for row in qs],
                "values": [row["total"] for row in qs]
            }
        )


# ---------------------------------------------
# DONUT CHART (Project Status - Optimized)
# ---------------------------------------------
class ProjectStatusAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):

        projects = Project.objects.annotate(
            total_tasks=Count("phases__tasks", distinct=True),
            completed_tasks=Count(
                "phases__tasks",
                filter=Q(phases__tasks__status="completed"),
                distinct=True
            ),
        ).annotate(
            computed_status=Case(
                When(total_tasks=0, then=Value("pending")),
                When(total_tasks=F("completed_tasks"), then=Value("completed")),
                default=Value("ongoing"),
                output_field=CharField(),
            )
        )

        total = projects.count()
        if not total:
            return api_response(
                success=True,
                message="Project status fetched successfully",
                data={"completed": 0, "ongoing": 0, "pending": 0}
            )

        completed = projects.filter(computed_status="completed").count()
        ongoing = projects.filter(computed_status="ongoing").count()
        pending = projects.filter(computed_status="pending").count()

        return api_response(
            success=True,
            message="Project status fetched successfully",
            data={
                "completed": round((completed / total) * 100, 2),
                "ongoing": round((ongoing / total) * 100, 2),
                "pending": round((pending / total) * 100, 2),
            }
        )