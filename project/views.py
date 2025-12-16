from rest_framework import viewsets, generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Project
from .serializers import ProjectSerializer
from .utils import api_response


# ---------------------------------------------------------
# Project CRUD using ModelViewSet
# ---------------------------------------------------------
class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by('-created_at')
    serializer_class = ProjectSerializer
    permission_classes = [AllowAny]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    # CREATE
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return api_response(
            success=True,
            message="Project created successfully",
            data=serializer.data,
            status_code=status.HTTP_201_CREATED
        )

    # UPDATE
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return api_response(
            success=True,
            message="Project updated successfully",
            data=serializer.data
        )

    # DELETE
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        return api_response(
            success=True,
            message="Project deleted successfully",
            data=None
        )

    # LIST
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return api_response(
            success=True,
            message="Projects fetched successfully",
            data=serializer.data
        )

    # RETRIEVE
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        return api_response(
            success=True,
            message="Project details fetched successfully",
            data=serializer.data
        )


# ---------------------------------------------------------
# Filter by Status (active / completed / not_started)
# ---------------------------------------------------------
class ProjectStatusFilterView(generics.ListAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        status_param = self.kwargs.get('status')
        return Project.objects.filter(status=status_param).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(
            queryset,
            many=True,
            context={"request": request}
        )

        return api_response(
            success=True,
            message=f"Projects filtered by status '{self.kwargs.get('status')}'",
            data=serializer.data
        )


# ---------------------------------------------------------
# Filter by Type (web / app / webapp)
# ---------------------------------------------------------
class ProjectTypeFilterView(generics.ListAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        ptype = self.kwargs.get('ptype')
        return Project.objects.filter(project_type=ptype).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(
            queryset,
            many=True,
            context={"request": request}
        )

        return api_response(
            success=True,
            message=f"Projects filtered by type '{self.kwargs.get('ptype')}'",
            data=serializer.data
        )
