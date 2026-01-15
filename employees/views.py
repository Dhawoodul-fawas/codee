from django.shortcuts import get_object_or_404
from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.generics import ListAPIView
from project.models import PhaseTask, Project

from .models import Employee
from .serializers import (
    EmployeeAllListSerializer,
    EmployeeBasicListSerializer,
    EmployeeListSerializer,
    EmployeeCreateUpdateSerializer,
    ManagerListSerializer,
)
from .utils import api_response


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all().order_by('-created_at')
    parser_classes = (MultiPartParser, FormParser)
    lookup_field = "employee_id"
    lookup_url_kwarg = "employee_id"

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    filterset_fields = ['status', 'department', 'employment_type', 'role', 'position', 'gender']
    search_fields = ['name', 'email', 'employee_id', 'phone']
    ordering_fields = ['created_at', 'joining_date', 'name']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return EmployeeListSerializer
        return EmployeeCreateUpdateSerializer


    # ▶ CREATE
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        read_serializer = EmployeeListSerializer(
            serializer.instance,
            context={"request": request}
        )

        return api_response(
            success=True,
            message="Employee created successfully",
            data=read_serializer.data,
            status_code=status.HTTP_201_CREATED
        )


    # ▶ UPDATE
    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            self.get_object(),
            data=request.data,
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        read_serializer = EmployeeListSerializer(
            serializer.instance,
            context={"request": request}
        )

        return api_response(
            success=True,
            message="Employee updated successfully",
            data=read_serializer.data
        )


    # ▶ DELETE
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        return api_response(
            success=True,
            message="Employee deleted successfully",
            data=None,
            status_code=status.HTTP_200_OK
        )


    # ▶ LIST with message
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        return api_response(
            success=True,
            message="Employee list fetched successfully",
            data=response.data
        )


    # ▶ RETRIEVE with message
    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)

        return api_response(
            success=True,
            message="Employee details fetched successfully",
            data=response.data
        )


# STAFF ONLY LIST
class EmployeeOnlyListView(generics.ListAPIView):
    serializer_class = EmployeeListSerializer

    def get_queryset(self):
        return Employee.objects.filter(employment_type="staff").order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True, context={"request": request})

        return api_response(
            success=True,
            message="Staff employees fetched successfully",
            data=serializer.data
        )


# ✅ INTERN ONLY FULL LIST
class InternOnlyListView(generics.ListAPIView):
    serializer_class = EmployeeListSerializer

    def get_queryset(self):
        return Employee.objects.filter(employment_type="intern").order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True, context={"request": request})

        return api_response(
            success=True,
            message="Intern employees fetched successfully",
            data=serializer.data
        )


# ✅ STAFF BASIC LIST
class StaffListView(generics.ListAPIView):
    serializer_class = EmployeeBasicListSerializer

    def get_queryset(self):
        return Employee.objects.filter(employment_type="staff").order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)

        return api_response(
            success=True,
            message="Staff basic list fetched successfully",
            data=serializer.data
        )


# ✅ INTERN BASIC LIST
class InternListView(generics.ListAPIView):
    serializer_class = EmployeeBasicListSerializer

    def get_queryset(self):
        return Employee.objects.filter(employment_type="intern").order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)

        return api_response(
            success=True,
            message="Intern basic list fetched successfully",
            data=serializer.data
        )

class EmployeeProjectCardView(APIView):

    def get(self, request, employee_id):
        employee = get_object_or_404(Employee, employee_id=employee_id)

        # All projects where this employee has tasks
        projects = Project.objects.filter(
            phases__tasks__assigned_to=employee
        ).distinct()

        assigned = projects.count()
        completed = 0
        pending = 0

        for project in projects:
            tasks = PhaseTask.objects.filter(
                phase__project=project,
                assigned_to=employee
            )

            if tasks.filter(status="pending").exists():
                pending += 1
            elif not tasks.exclude(status="completed").exists():
                completed += 1

        data = {
            "assigned": assigned,
            "completed": completed,
            "pending": pending,
        }

        return Response(data)    

class EmployeeFullDetailAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, employee_id):
        employee = get_object_or_404(Employee, employee_id=employee_id)

        serializer = EmployeeListSerializer(
            employee,
            context={"request": request}
        )

        # Get all assigned projects
        projects = Project.objects.filter(team_members=employee).prefetch_related("phases")

        assigned = projects.count()
        completed = 0
        pending = 0

        # Use same logic as serializer
        for p in projects:
            tasks = p.phases.all().values_list("tasks__status", flat=True)

            if not tasks:
                pending += 1
            elif all(status == "completed" for status in tasks):
                completed += 1
            else:
                pending += 1

        return api_response(
            True,
            "Employee details fetched successfully",
            {
                "employee": serializer.data,
                "project_cards": {
                    "assigned": assigned,
                    "completed": completed,
                    "pending": pending
                }
            }
        )

class ManagerListAPIView(ListAPIView):
    serializer_class = ManagerListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Employee.objects.filter(
            employment_type="staff",
            is_manager=True,
            status="active"
        ).order_by("name")        