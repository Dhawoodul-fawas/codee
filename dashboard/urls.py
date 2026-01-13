from django.urls import path
from .views import (
    DashboardSummaryAPIView,
    OngoingProjectsAPIView,
    PerformanceGraphAPIView,
    ProjectStatusAPIView
)

urlpatterns = [
    path("summary/", DashboardSummaryAPIView.as_view()),
    path("ongoing-projects/", OngoingProjectsAPIView.as_view()),
    path("performance-graph/", PerformanceGraphAPIView.as_view()),
    path("project-status/", ProjectStatusAPIView.as_view()),
]
