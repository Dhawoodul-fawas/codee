from django.urls import path
from .views import EmployeeFullDetailAPIView, EmployeeOnlyListView, EmployeeProjectCardView, EmployeeViewSet, InternListView, InternOnlyListView, ManagerListAPIView, StaffListView

employee_create = EmployeeViewSet.as_view({
    'post': 'create',
})

employee_edit = EmployeeViewSet.as_view({'patch': 'partial_update',})
employee_delete = EmployeeViewSet.as_view({'delete': 'destroy',})

urlpatterns = [
    path('emp/', employee_create, name='employee-create'),
    path('emp-edit/<str:employee_id>/',employee_edit,name='emp_edit'),
    path('emp-delete/<str:employee_id>/',employee_delete,name='emp_delete'),
    path('emp-list/', EmployeeOnlyListView.as_view(), name='employee-list'),
    path('interns-list/', InternOnlyListView.as_view(), name='intern-list'),
    path('employees/basic/', StaffListView.as_view(), name='employee-basic-list'),

    path('interns/basic/', InternListView.as_view(), name='intern-basic-list'),

    path('employees/<int:employee_id>/project-cards/',EmployeeProjectCardView.as_view(),name='employee-project-cards'
    ),

    path(
        'employee/full/<str:employee_id>/',
        EmployeeFullDetailAPIView.as_view(),
        name='employee-full-detail'
    ),

    path(
        'employees/managers/',
        ManagerListAPIView.as_view(),
        name='manager-list'
    ),
]





