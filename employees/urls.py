from django.urls import path
from .views import EmployeeFullDetailAPIView, EmployeeOnlyListView, EmployeeProjectCardView, EmployeeViewSet, InternListView, InternOnlyListView, StaffListView

employee_create = EmployeeViewSet.as_view({
    'post': 'create',
})

employee_detail = EmployeeViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
})

urlpatterns = [
    path('emp/', employee_create, name='employee_create'), 
    path('empl/<str:employee_id>/', employee_detail, name='employee_detail'),
    path('emp-list/', EmployeeOnlyListView.as_view(), name='employee_all_list'),
    path('interns-list/', InternOnlyListView.as_view(), name='employee_all_list'),
    path("employees/basic/", StaffListView.as_view(), name="employee-basic-list"),
    path('interns/basic/', InternListView.as_view(), name="interns-basic-list"),
    path("employees/<int:employee_id>/project-cards/",EmployeeProjectCardView.as_view()),
    path("employee/full/<str:employee_id>/", EmployeeFullDetailAPIView.as_view()),


]
