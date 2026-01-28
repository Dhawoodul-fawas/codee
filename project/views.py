from django.shortcuts import get_object_or_404
from rest_framework import viewsets, generics, status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from .models import (
    Project,
    ProjectPhase,
    PhaseTask,
)

from .serializers import (
    ProjectSerializer,
    ProjectListSerializer,
    ProjectPhaseSerializer,
    PhaseTaskSerializer,
)

from .utils import api_response


# =====================================================
# PROJECT VIEWSET (CRUD)
# =====================================================

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by('-created_at')
    permission_classes = [AllowAny]
    lookup_field = "project_id"
    lookup_url_kwarg = "project_id"

    def get_serializer_class(self):
        return (
            ProjectListSerializer
            if self.action == "list"
            else ProjectSerializer
        )

    def get_serializer_context(self):
        return {"request": self.request}

    # -----------------------------
    # LIST
    # -----------------------------
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

    # -----------------------------
    # CREATE
    # -----------------------------
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

    # -----------------------------
    # RETRIEVE
    # -----------------------------
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

    # -----------------------------
    # UPDATE (PATCH)
    # -----------------------------
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

    # -----------------------------
    # DELETE
    # -----------------------------
    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return api_response(
            success=True,
            message="Project deleted successfully",
            data=None
        )


# =====================================================
# PROJECT FILTER BY TYPE
# =====================================================

class ProjectTypeFilterView(generics.ListAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Project.objects.filter(
            project_type=self.kwargs["ptype"]
        ).order_by("-created_at")

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


# =====================================================
# PROJECT PHASE VIEWSET
# =====================================================

class ProjectPhaseViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectPhaseSerializer
    permission_classes = [AllowAny]

    queryset = ProjectPhase.objects.all()

    lookup_field = "phase_id"
    lookup_url_kwarg = "phase_id"

    # -----------------------------
    # LIST BY PROJECT (PATH PARAM)
    # -----------------------------
    def list(self, request, *args, **kwargs):
        project_id = kwargs.get("project_id")

        if project_id:
            get_object_or_404(Project, project_id=project_id)

            queryset = ProjectPhase.objects.filter(
                project__project_id=project_id
            ).order_by("start_date")
        else:
            queryset = ProjectPhase.objects.all().order_by("start_date")

        serializer = self.get_serializer(
            queryset,
            many=True,
            context={"request": request}
        )

        return api_response(
            success=True,
            message="Project phases fetched successfully",
            data=serializer.data
        )

    # -----------------------------
    # CREATE
    # -----------------------------
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

    # -----------------------------
    # UPDATE ✅
    # -----------------------------
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
            message="Phase updated successfully",
            data=serializer.data
        )

    # -----------------------------
    # DELETE ✅
    # -----------------------------
    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return api_response(
            success=True,
            message="Phase deleted successfully",
            data=None
        )

# =====================================================
# PHASE TASK VIEWSET
# =====================================================

class PhaseTaskViewSet(viewsets.ModelViewSet):
    serializer_class = PhaseTaskSerializer
    permission_classes = [AllowAny]

    queryset = PhaseTask.objects.select_related(
        "phase",
        "phase__project"
    )

    lookup_field = "task_id"
    lookup_url_kwarg = "task_id"

    # -----------------------------
    # LIST TASKS BY PHASE (PATH)
    # -----------------------------
    def list(self, request, *args, **kwargs):
        phase_id = kwargs.get("phase_id")

        if phase_id:
            get_object_or_404(ProjectPhase, phase_id=phase_id)

            queryset = PhaseTask.objects.filter(
                phase__phase_id=phase_id
            ).order_by("start_date")
        else:
            queryset = PhaseTask.objects.all().order_by("start_date")

        serializer = self.get_serializer(
            queryset,
            many=True,
            context={"request": request}
        )

        return api_response(
            success=True,
            message="Phase tasks fetched successfully",
            data=serializer.data
        )

    # -----------------------------
    # CREATE
    # -----------------------------
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

    # -----------------------------
    # UPDATE ✅ (THIS WAS MISSING)
    # -----------------------------
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
            message="Task updated successfully",
            data=serializer.data
        )

    # -----------------------------
    # DELETE ✅ (THIS WAS MISSING)
    # -----------------------------
    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return api_response(
            success=True,
            message="Task deleted successfully",
            data=None
        )

# =====================================================
# PROJECT FULL DETAIL API
# =====================================================

class ProjectFullDetailAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, project_id):
        project = get_object_or_404(
            Project,
            project_id=project_id
        )

        project_data = ProjectSerializer(
            project,
            context={"request": request}
        ).data

        phases = (
            ProjectPhase.objects
            .filter(project=project)
            .prefetch_related(
                "tasks",
                "tasks__assigned_to"
            )
        )

        phase_data = []
        total_tasks = 0
        completed_tasks = 0

        for phase in phases:
            tasks = phase.tasks.all()

            total_tasks += tasks.count()
            completed_tasks += tasks.filter(
                status="completed"
            ).count()

            phase_data.append({
                "id": phase.id,
                "phase_id": phase.phase_id,
                "phase_type": phase.phase_type,
                "description": phase.description,
                "start_date": phase.start_date,
                "end_date": phase.end_date,
                "tasks": PhaseTaskSerializer(
                    tasks,
                    many=True,
                    context={"request": request}
                ).data
            })

        progress = (
            int((completed_tasks / total_tasks) * 100)
            if total_tasks else 0
        )

        return api_response(
            success=True,
            message="Project full details fetched successfully",
            data={
                "project": project_data,
                "phases": phase_data,
                "progress_percent": progress
            }
        )
