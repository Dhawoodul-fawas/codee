from django.urls import path
from .views import (

    # Project
    ProjectViewSet,
    ProjectTypeFilterView,

    # Planning - Project
    ProjectPlanningCreateAPIView,
    ProjectPlanningListAPIView,
    ProjectPlanningDetailAPIView,

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
    path(
        'projects/filter/type/<str:ptype>/',
        ProjectTypeFilterView.as_view(),
        name='project-filter-type'
    ),

    # -----------------------------
    # Project Planning
    # -----------------------------
    path(
        'project-planning/create/',
        ProjectPlanningCreateAPIView.as_view(),
        name='project-planning-create'
    ),
    path(
        'project-planning/list/',
        ProjectPlanningListAPIView.as_view(),
        name='project-planning-list'
    ),
    path(
        'project-planning/edit/<int:pk>/',
        ProjectPlanningDetailAPIView.as_view(),
        name='project-planning-detail'
    ),

    # -----------------------------
    # Design Planning
    # -----------------------------
    path(
        'design-planning/create/',
        DesignPlanningCreateAPIView.as_view(),
        name='design-planning-create'
    ),
    path(
        'design-planning/list/',
        DesignPlanningListAPIView.as_view(),
        name='design-planning-list'
    ),
    path(
        'design-planning/edit/<int:pk>/',
        DesignPlanningDetailAPIView.as_view(),
        name='design-planning-detail'
    ),

    # -----------------------------
    # Development Planning
    # -----------------------------
    path(
        'development-planning/create/',
        DevelopmentPlanningCreateAPIView.as_view(),
        name='development-planning-create'
    ),
    path(
        'development-planning/list/',
        DevelopmentPlanningListAPIView.as_view(),
        name='development-planning-list'
    ),
    path(
        'development-planning/edit/<int:pk>/',
        DevelopmentPlanningDetailAPIView.as_view(),
        name='development-planning-detail'
    ),

    # -----------------------------
    # Testing Planning
    # -----------------------------
    path(
        'testing-planning/create/',
        TestingPlanningCreateAPIView.as_view(),
        name='testing-planning-create'
    ),
    path(
        'testing-planning/list/',
        TestingPlanningListAPIView.as_view(),
        name='testing-planning-list'
    ),
    path(
        'testing-planning/edit/<int:pk>/',
        TestingPlanningDetailAPIView.as_view(),
        name='testing-planning-detail'
    ),

    # -----------------------------
    # Deployment Planning
    # -----------------------------
    path(
        'deployment-planning/create/',
        DeploymentPlanningCreateAPIView.as_view(),
        name='deployment-planning-create'
    ),
    path(
        'deployment-planning/list/',
        DeploymentPlanningListAPIView.as_view(),
        name='deployment-planning-list'
    ),
    path(
        'deployment-planning/edit/<int:pk>/',
        DeploymentPlanningDetailAPIView.as_view(),
        name='deployment-planning-detail'
    ),


]
