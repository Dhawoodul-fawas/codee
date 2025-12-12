from django.urls import path
from .views import AdminAttendanceList

urlpatterns = [
    path('admin-attendance/', AdminAttendanceList.as_view(), name='admin-attendance'),
]
