from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, generics, status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from .models import (
    PhaseTask,
    Project,
    ProjectPhase,
   
)

from .serializers import (
    PhaseTaskSerializer, ProjectListSerializer, ProjectPhaseSerializer, ProjectSerializer,
    
)

from .utils import api_response


# ---------------------------------------------------------
# Project CRUD using ModelViewSet
# ---------------------------------------------------------
class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by('-created_at')
    permission_classes = [AllowAny]
    lookup_field = "project_id"
    lookup_url_kwarg = "project_id"

    def get_serializer_class(self):
        return ProjectListSerializer if self.action == 'list' else ProjectSerializer

    def get_serializer_context(self):
        return {"request": self.request}

    # ✅ FIX: LIST RESPONSE WRAPPED
    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            self.get_queryset(),
            many=True,
            context={"request": request}
        )
        return api_response(
            success=True,
            message="Projects fetched successfully",
            data=serializer.data
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return api_response(
            success=True,
            message="Project created successfully",
            data=serializer.data,
            status_code=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            self.get_object(),
            data=request.data,
            partial=True,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return api_response(
            success=True,
            message="Project updated successfully",
            data=serializer.data
        )

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            self.get_object(),
            context={"request": request}
        )
        return api_response(
            success=True,
            message="Project details fetched successfully",
            data=serializer.data
        )

    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return api_response(
            success=True,
            message="Project deleted successfully",
            data=None
        )



# ---------------------------------------------------------
# Filter by Type (web / app / webapp)
# ---------------------------------------------------------
class ProjectTypeFilterView(generics.ListAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Project.objects.filter(
            project_type=self.kwargs['ptype']
        ).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            self.get_queryset(),
            many=True,
            context={"request": request}
        )
        return api_response(
            success=True,
            message=f"Projects filtered by type '{self.kwargs['ptype']}'",
            data=serializer.data
        )

class ProjectPhaseViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectPhaseSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        project_id = self.kwargs.get("project_id")
        return ProjectPhase.objects.filter(
            project__project_id=project_id
        )

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            self.get_queryset(),
            many=True,
            context={"request": request}
        )
        return api_response(
            success=True,
            message="Project phases fetched successfully",
            data=serializer.data
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return api_response(
            success=True,
            message="Phase added successfully",
            data=serializer.data,
            status_code=status.HTTP_201_CREATED
    )


        return api_response(
            success=True,
            message="Phase added successfully",
            data=serializer.data,
            status_code=status.HTTP_201_CREATED
        )



class PhaseTaskViewSet(viewsets.ModelViewSet):
    serializer_class = PhaseTaskSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        phase_id = self.request.query_params.get("phase")

        queryset = PhaseTask.objects.select_related(
            "phase",
            "phase__project"
        )

        if phase_id:
            queryset = queryset.filter(phase__phase_id=phase_id)


        return queryset


    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            self.get_queryset(),
            many=True,
            context={"request": request}
        )
        return api_response(
            success=True,
            message="Tasks fetched successfully",
            data=serializer.data
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return api_response(
            success=True,
            message="Task added successfully",
            data=serializer.data,
            status_code=status.HTTP_201_CREATED
        )


class ProjectFullDetailAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, project_id):
        project = get_object_or_404(Project, project_id=project_id)

        project_data = ProjectSerializer(
            project,
            context={"request": request}
        ).data

        phases = ProjectPhase.objects.filter(project=project).prefetch_related(
        "tasks",
        "tasks__assigned_to"
)


        phase_data = []
        total_tasks = 0
        completed_tasks = 0

        for phase in phases:
            tasks = phase.tasks.all()

            total_tasks += tasks.count()
            completed_tasks += tasks.filter(status="completed").count()

            phase_data.append({
                "id": phase.id,
                "phase_type": phase.phase_type,
                "description": phase.description,
                "start_date": phase.start_date,
                "end_date": phase.end_date,
                "tasks":PhaseTaskSerializer(tasks,many=True,context={"request": request}).data

            })

        progress = int((completed_tasks / total_tasks) * 100) if total_tasks else 0

        return api_response(
            success=True,
            message="Project full details fetched successfully",
            data={
                "project": project_data,
                "phases": phase_data,
                "progress_percent": progress
            }
        )
