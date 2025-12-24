from django.urls import path
from .views import (
    DesignPlanningCreateAPIView,
    DesignPlanningDetailAPIView,
    DesignPlanningListAPIView,
    ProjectPlanningCreateAPIView,
    ProjectPlanningDetailAPIView,
    ProjectPlanningListAPIView,
    ProjectViewSet,
    ProjectStatusFilterView,
    ProjectTypeFilterView,
    ProjectBudgetViewSet,
    # Design
    DesignPlanningCreateAPIView,
    DesignPlanningListAPIView,
    DesignPlanningDetailAPIView,

    # Development
    DevelopmentPlanningCreateAPIView,
    DevelopmentPlanningListAPIView,
    DevelopmentPlanningDetailAPIView,

    # Testing
    TestingPlanningCreateAPIView,
    TestingPlanningListAPIView,
    TestingPlanningDetailAPIView,

    # Deployment
    DeploymentPlanningCreateAPIView,
    DeploymentPlanningListAPIView,
    DeploymentPlanningDetailAPIView,
)

# -----------------------------
# Project ViewSet mappings
# -----------------------------
project_create = ProjectViewSet.as_view({"post": "create"})
project_list = ProjectViewSet.as_view({"get": "list"})
project_detail = ProjectViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy"
})

# -----------------------------
# Project Budget ViewSet mappings
# -----------------------------
project_budget_create = ProjectBudgetViewSet.as_view({"post": "create"})

# LIST
project_budget_list = ProjectBudgetViewSet.as_view({"get": "list"})

# DETAIL / UPDATE / DELETE
project_budget_detail = ProjectBudgetViewSet.as_view({
    "get": "retrieve",
    "patch": "update",
    "put": "update",
    "delete": "destroy"
})

# project/urls.py

project_planning_create = ProjectPlanningCreateAPIView.as_view()
project_planning_list = ProjectPlanningListAPIView.as_view()
project_planning_detail = ProjectPlanningDetailAPIView.as_view()

design_planning_create = DesignPlanningCreateAPIView.as_view()
design_planning_list = DesignPlanningListAPIView.as_view()
design_planning_detail = DesignPlanningDetailAPIView.as_view()


urlpatterns = [

    # -----------------------------
    # Projects
    # -----------------------------
    path('projects/create/', project_create, name='project-create'),
    path('projects/list/', project_list, name='project-list'),
    path('projects/basic/', project_list, name='project-basic-list'),

    path('projects/edit/<int:pk>/', project_detail, name='project-detail'),

    # -----------------------------
    # Project Filters
    # -----------------------------
    path('projects/filter/status/<str:status>/',ProjectStatusFilterView.as_view(),name='project-filter-status'),
    path('projects/filter/type/<str:ptype>/',ProjectTypeFilterView.as_view(),name='project-filter-type'),

    # -----------------------------
    # Project Budget
    # -----------------------------
    path('project-budgets/create/',project_budget_create,name='project-budget-create'),
    path('project-budgets/list/',project_budget_list,name='project-budget-list'),
    path('project-budgets/edit/<int:pk>/',project_budget_detail,name='project-budget-detail'),

    # project/urls.py

    path('project-planning/create/', project_planning_create, name='project-planning-create'),
    path('project-planning/list/', project_planning_list, name='project-planning-list'),
    path('project-planning/edit/<int:pk>/', project_planning_detail, name='project-planning-detail'),

    path('design-planning/create/', design_planning_create, name='design-planning-create'),
    path('design-planning/list/', design_planning_list, name='design-planning-list'),
    path('design-planning/edit/<int:pk>/', design_planning_detail, name='design-planning-detail'),

    path("development-planning/create/", DevelopmentPlanningCreateAPIView.as_view()),
    path("development-planning/list/", DevelopmentPlanningListAPIView.as_view()),
    path("development-planning/edit/<int:pk>/", DevelopmentPlanningDetailAPIView.as_view()),

    # Testing
    path("testing-planning/create/", TestingPlanningCreateAPIView.as_view()),
    path("testing-planning/list/", TestingPlanningListAPIView.as_view()),
    path("testing-planning/edit/<int:pk>/", TestingPlanningDetailAPIView.as_view()),

    # Deployment
    path("deployment-planning/create/", DeploymentPlanningCreateAPIView.as_view()),
    path("deployment-planning/list/", DeploymentPlanningListAPIView.as_view()),
    path("deployment-planning/edit/<int:pk>/", DeploymentPlanningDetailAPIView.as_view()),


]