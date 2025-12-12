from django.urls import path
from .views import DashboardSummaryAPIView, OngoingProjectsAPIView, PerformanceGraphAPIView, ProjectStatusAPIView

urlpatterns = [
    path("summary/", DashboardSummaryAPIView.as_view(), name="dashboard-summary"),
    path("ongoing-projects/", OngoingProjectsAPIView.as_view(), name="dashboard-ongoing-projects"),
    path("performance-graph/", PerformanceGraphAPIView.as_view(), name="dashboard-performance-graph"),
    path("project-status/", ProjectStatusAPIView.as_view(), name="dashboard-project-status"),
]
