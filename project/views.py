from rest_framework import viewsets, generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import DeploymentPlanning, DesignPlanning, DevelopmentPlanning, Project, ProjectBudget, ProjectPlanning, TestingPlanning
from .serializers import   DeploymentPlanningSerializer, DesignPlanningSerializer, DevelopmentPlanningSerializer, ProjectBasicListSerializer, ProjectBudgetSerializer, ProjectPlanningSerializer,ProjectSerializer, TestingPlanningSerializer
from .utils import api_response


# ---------------------------------------------------------
# Project CRUD using ModelViewSet
# ---------------------------------------------------------
class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by('-created_at')
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectBasicListSerializer
        return ProjectSerializer

    def get_serializer_context(self):
        return {"request": self.request}

    # CREATE
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

    # UPDATE
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
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

    # DELETE
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()

        return api_response(
            success=True,
            message="Project deleted successfully",
            data=None
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


class ProjectBudgetViewSet(viewsets.ModelViewSet):
    queryset = ProjectBudget.objects.all()
    serializer_class = ProjectBudgetSerializer
    permission_classes = [AllowAny]

    # CREATE
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

    # UPDATE / PATCH
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
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

    # RETRIEVE
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        return api_response(
            success=True,
            message="Project budget details fetched successfully",
            data=serializer.data
        )

    # LIST
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return api_response(
            success=True,
            message="Project budgets fetched successfully",
            data=serializer.data
        )

    # DELETE
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()

        return api_response(
            success=True,
            message="Project budget deleted successfully",
            data=None
        )

class ProjectPlanningCreateAPIView(generics.CreateAPIView):
    queryset = ProjectPlanning.objects.all()
    serializer_class = ProjectPlanningSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        project_id = request.data.get("project_id")

        # prevent duplicate planning
        if ProjectPlanning.objects.filter(project_id=project_id).exists():
            return api_response(
                success=False,
                message="Planning already exists for this project",
                data=None,
                status_code=400
            )

        serializer = self.get_serializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return api_response(
            success=True,
            message="Project planning created successfully",
            data=serializer.data,
            status_code=201
        )


# LIST
class ProjectPlanningListAPIView(generics.ListAPIView):
    queryset = ProjectPlanning.objects.all().order_by('-created_at')
    serializer_class = ProjectPlanningSerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            self.get_queryset(),
            many=True,
            context={"request": request}
        )

        return api_response(
            success=True,
            message="Project planning list fetched successfully",
            data=serializer.data
        )


# RETRIEVE / UPDATE / DELETE
class ProjectPlanningDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProjectPlanning.objects.all()
    serializer_class = ProjectPlanningSerializer
    permission_classes = [AllowAny]

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            self.get_object(),
            context={"request": request}
        )

        return api_response(
            success=True,
            message="Project planning details fetched",
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
            message="Project planning updated successfully",
            data=serializer.data
        )

    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()

        return api_response(
            success=True,
            message="Project planning deleted successfully",
            data=None
        )

# class DesignPlanningCreateAPIView(generics.CreateAPIView):
#     queryset = DesignPlanning.objects.all()
#     serializer_class = DesignPlanningSerializer
#     permission_classes = [AllowAny]

#     def create(self, request, *args, **kwargs):
#         project_id = request.data.get("project_id")

#         if DesignPlanning.objects.filter(project_id=project_id).exists():
#             return api_response(
#                 success=False,
#                 message="Design planning already exists for this project",
#                 data=None,
#                 status_code=status.HTTP_400_BAD_REQUEST
#             )

#         serializer = self.get_serializer(
#             data=request.data,
#             context={"request": request}
#         )
#         serializer.is_valid(raise_exception=True)
#         serializer.save()

#         return api_response(
#             success=True,
#             message="Design planning created successfully",
#             data=serializer.data,
#             status_code=status.HTTP_201_CREATED
#         )


# # LIST
# class DesignPlanningListAPIView(generics.ListAPIView):
#     queryset = DesignPlanning.objects.all().order_by('-created_at')
#     serializer_class = DesignPlanningSerializer
#     permission_classes = [AllowAny]

#     def list(self, request, *args, **kwargs):
#         serializer = self.get_serializer(
#             self.get_queryset(),
#             many=True,
#             context={"request": request}
#         )

#         return api_response(
#             success=True,
#             message="Design planning list fetched successfully",
#             data=serializer.data
#         )


# # DETAIL / UPDATE / DELETE
# class DesignPlanningDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = DesignPlanning.objects.all()
#     serializer_class = DesignPlanningSerializer
#     permission_classes = [AllowAny]

#     def retrieve(self, request, *args, **kwargs):
#         serializer = self.get_serializer(
#             self.get_object(),
#             context={"request": request}
#         )

#         return api_response(
#             success=True,
#             message="Design planning details fetched",
#             data=serializer.data
#         )

#     def update(self, request, *args, **kwargs):
#         serializer = self.get_serializer(
#             self.get_object(),
#             data=request.data,
#             partial=True,
#             context={"request": request}
#         )
#         serializer.is_valid(raise_exception=True)
#         serializer.save()

#         return api_response(
#             success=True,
#             message="Design planning updated successfully",
#             data=serializer.data
#         )

#     def destroy(self, request, *args, **kwargs):
#         self.get_object().delete()

#         return api_response(
#             success=True,
#             message="Design planning deleted successfully",
#             data=None
#         )    




class BasePlanningAPIView:
    """
    Reusable base class for Create, List, Detail, Update, Delete
    """

    permission_classes = [AllowAny]

    # -------- CREATE --------
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

    # -------- LIST --------
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

    # -------- RETRIEVE --------
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

    # -------- UPDATE --------
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

    # -------- DELETE --------
    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()

        return api_response(
            success=True,
            message=f"{self.planning_name} deleted successfully",
            data=None
        )
    
class DesignPlanningCreateAPIView(BasePlanningAPIView, generics.CreateAPIView):
    queryset = DesignPlanning.objects.all()
    serializer_class = DesignPlanningSerializer
    planning_name = "Design planning"


class DesignPlanningListAPIView(BasePlanningAPIView, generics.ListAPIView):
    queryset = DesignPlanning.objects.all().order_by("-created_at")
    serializer_class = DesignPlanningSerializer
    planning_name = "Design planning"


class DesignPlanningDetailAPIView(
    BasePlanningAPIView,
    generics.RetrieveUpdateDestroyAPIView
):
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


class DevelopmentPlanningDetailAPIView(
    BasePlanningAPIView,
    generics.RetrieveUpdateDestroyAPIView
):
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


class TestingPlanningDetailAPIView(
    BasePlanningAPIView,
    generics.RetrieveUpdateDestroyAPIView
):
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


class DeploymentPlanningDetailAPIView(
    BasePlanningAPIView,
    generics.RetrieveUpdateDestroyAPIView
):
    queryset = DeploymentPlanning.objects.all()
    serializer_class = DeploymentPlanningSerializer
    planning_name = "Deployment planning"

