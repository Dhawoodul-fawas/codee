from django.urls import path
from .views import (
    ApkLoginView,
    CheckInOutView,
    ApplyLeaveView,
    HomeAttendanceStatusView,
    AttendanceListView,
    LeaveListView,
    LoginListView,
    LogoutView
)

urlpatterns = [
    path("login/", ApkLoginView.as_view()),
    path('apk/login-list/', LoginListView.as_view()),
    path('logout/', LogoutView.as_view(), name='logout'),
    path("check/", CheckInOutView.as_view()),
    path('apply-leave/', ApplyLeaveView.as_view(), name='apply-leave'),
    path('leave-list/', LeaveListView.as_view(), name='leave-list'),
    path("home-status/", HomeAttendanceStatusView.as_view()),
    path("attendance-list/", AttendanceListView.as_view()),
    
]
