from rest_framework import viewsets, generics, status
from rest_framework.permissions import AllowAny

from .models import (
    Project, ProjectBudget,
    ProjectPlanning, DesignPlanning,
    DevelopmentPlanning, TestingPlanning,
    DeploymentPlanning
)

from .serializers import (
    ProjectSerializer, ProjectBasicListSerializer,
    ProjectBudgetSerializer,
    ProjectPlanningSerializer, DesignPlanningSerializer,
    DevelopmentPlanningSerializer, TestingPlanningSerializer,
    DeploymentPlanningSerializer
)

from .utils import api_response



# ---------------------------------------------------------
# Project CRUD using ModelViewSet
# ---------------------------------------------------------
class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by('-created_at')
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        return ProjectBasicListSerializer if self.action == 'list' else ProjectSerializer

    def get_serializer_context(self):
        return {"request": self.request}

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
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
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return api_response(
            success=True,
            message="Project updated successfully",
            data=serializer.data
        )

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
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



class ProjectBudgetViewSet(viewsets.ModelViewSet):
    queryset = ProjectBudget.objects.all()
    serializer_class = ProjectBudgetSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return api_response(
            success=True,
            message="Project budget created successfully",
            data=serializer.data,
            status_code=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            self.get_object(),
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return api_response(
            success=True,
            message="Project budget updated successfully",
            data=serializer.data
        )

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return api_response(
            success=True,
            message="Project budget fetched successfully",
            data=serializer.data
        )

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return api_response(
            success=True,
            message="Project budgets fetched successfully",
            data=serializer.data
        )

    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return api_response(
            success=True,
            message="Project budget deleted successfully",
            data=None
        )

class BasePlanningAPIView:
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        project_id = request.data.get("project_id")

        if self.queryset.filter(project_id=project_id).exists():
            return api_response(
                success=False,
                message=f"{self.planning_name} already exists for this project",
                data=None,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return api_response(
            success=True,
            message=f"{self.planning_name} created successfully",
            data=serializer.data,
            status_code=status.HTTP_201_CREATED
        )

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            self.get_queryset(),
            many=True,
            context={"request": request}
        )
        return api_response(
            success=True,
            message=f"{self.planning_name} list fetched successfully",
            data=serializer.data
        )

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            self.get_object(),
            context={"request": request}
        )
        return api_response(
            success=True,
            message=f"{self.planning_name} details fetched",
            data=serializer.data
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
            message=f"{self.planning_name} updated successfully",
            data=serializer.data
        )

    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return api_response(
            success=True,
            message=f"{self.planning_name} deleted successfully",
            data=None
        )


class ProjectPlanningCreateAPIView(BasePlanningAPIView, generics.CreateAPIView):
    queryset = ProjectPlanning.objects.all()
    serializer_class = ProjectPlanningSerializer
    planning_name = "Project planning"


class ProjectPlanningListAPIView(BasePlanningAPIView, generics.ListAPIView):
    queryset = ProjectPlanning.objects.all().order_by("-created_at")
    serializer_class = ProjectPlanningSerializer
    planning_name = "Project planning"


class ProjectPlanningDetailAPIView(BasePlanningAPIView, generics.RetrieveUpdateDestroyAPIView):
    queryset = ProjectPlanning.objects.all()
    serializer_class = ProjectPlanningSerializer
    planning_name = "Project planning"



class DesignPlanningCreateAPIView(BasePlanningAPIView, generics.CreateAPIView):
    queryset = DesignPlanning.objects.all()
    serializer_class = DesignPlanningSerializer
    planning_name = "Design planning"


class DesignPlanningListAPIView(BasePlanningAPIView, generics.ListAPIView):
    queryset = DesignPlanning.objects.all().order_by("-created_at")
    serializer_class = DesignPlanningSerializer
    planning_name = "Design planning"


class DesignPlanningDetailAPIView(BasePlanningAPIView, generics.RetrieveUpdateDestroyAPIView):
    queryset = DesignPlanning.objects.all()
    serializer_class = DesignPlanningSerializer
    planning_name = "Design planning"

    

class DevelopmentPlanningCreateAPIView(BasePlanningAPIView, generics.CreateAPIView):
    queryset = DevelopmentPlanning.objects.all()
    serializer_class = DevelopmentPlanningSerializer
    planning_name = "Development planning"


class DevelopmentPlanningListAPIView(BasePlanningAPIView, generics.ListAPIView):
    queryset = DevelopmentPlanning.objects.all().order_by("-created_at")
    serializer_class = DevelopmentPlanningSerializer
    planning_name = "Development planning"


class DevelopmentPlanningDetailAPIView(BasePlanningAPIView, generics.RetrieveUpdateDestroyAPIView):
    queryset = DevelopmentPlanning.objects.all()
    serializer_class = DevelopmentPlanningSerializer
    planning_name = "Development planning"



class TestingPlanningCreateAPIView(BasePlanningAPIView, generics.CreateAPIView):
    queryset = TestingPlanning.objects.all()
    serializer_class = TestingPlanningSerializer
    planning_name = "Testing planning"


class TestingPlanningListAPIView(BasePlanningAPIView, generics.ListAPIView):
    queryset = TestingPlanning.objects.all().order_by("-created_at")
    serializer_class = TestingPlanningSerializer
    planning_name = "Testing planning"


class TestingPlanningDetailAPIView(BasePlanningAPIView, generics.RetrieveUpdateDestroyAPIView):
    queryset = TestingPlanning.objects.all()
    serializer_class = TestingPlanningSerializer
    planning_name = "Testing planning"


class DeploymentPlanningCreateAPIView(BasePlanningAPIView, generics.CreateAPIView):
    queryset = DeploymentPlanning.objects.all()
    serializer_class = DeploymentPlanningSerializer
    planning_name = "Deployment planning"


class DeploymentPlanningListAPIView(BasePlanningAPIView, generics.ListAPIView):
    queryset = DeploymentPlanning.objects.all().order_by("-created_at")
    serializer_class = DeploymentPlanningSerializer
    planning_name = "Deployment planning"


class DeploymentPlanningDetailAPIView(BasePlanningAPIView, generics.RetrieveUpdateDestroyAPIView):
    queryset = DeploymentPlanning.objects.all()
    serializer_class = DeploymentPlanningSerializer
    planning_name = "Deployment planning"


