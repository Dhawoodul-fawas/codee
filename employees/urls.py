from django.urls import path
from .views import EmployeeAndInternAllListAPIView, EmployeeFullDetailAPIView, EmployeeOnlyListView, EmployeeViewSet, InternOnlyListView, ManagerListAPIView

employee_create = EmployeeViewSet.as_view({
    'post': 'create',
})

employee_edit = EmployeeViewSet.as_view({'patch': 'partial_update',})
employee_delete = EmployeeViewSet.as_view({'delete': 'destroy',})

urlpatterns = [
    path('emp/', employee_create, name='employee-create'),
    path('emp-edit/<str:employee_id>/',employee_edit,name='emp_edit'),
    path('emp-delete/<str:employee_id>/',employee_delete,name='emp_delete'),
    path("employees-interns/all/",EmployeeAndInternAllListAPIView.as_view(),name="employee-intern-all-list"),

    path('emp-list/', EmployeeOnlyListView.as_view(), name='employee-list'),
    path('interns-list/', InternOnlyListView.as_view(), name='intern-list'),
    path('employee/full/<str:employee_id>/',EmployeeFullDetailAPIView.as_view(),name='employee-full-detail'),
    path('employees/managers/',ManagerListAPIView.as_view(),name='manager-list'),
]





