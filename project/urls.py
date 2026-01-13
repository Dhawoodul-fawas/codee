from django.urls import path
from .views import (

    # Project
    PhaseTaskViewSet,
    ProjectFullDetailAPIView,
    ProjectPhaseViewSet,
    ProjectViewSet,
    ProjectTypeFilterView,

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
# Phase ViewSet mappings
# -----------------------------
phase_create = ProjectPhaseViewSet.as_view({"post": "create"})
phase_list = ProjectPhaseViewSet.as_view({"get": "list"})
phase_detail = ProjectPhaseViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy"
})

# -----------------------------
# Task ViewSet mappings
# -----------------------------
task_create = PhaseTaskViewSet.as_view({"post": "create"})
task_list = PhaseTaskViewSet.as_view({"get": "list"})
task_detail = PhaseTaskViewSet.as_view({
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
    path('projects/edit/<str:project_id>/', project_detail, name='project-detail'),
    path("projects/full/<str:project_id>/", ProjectFullDetailAPIView.as_view()),

    # -----------------------------
    # Project Filters
    # -----------------------------
    path(
        'projects/filter/type/<str:ptype>/',
        ProjectTypeFilterView.as_view(),
        name='project-filter-type'
    ),

    # Project Phases
    # -----------------------------
    path('phases/create/', phase_create, name='phase-create'),
    path('phases/list/', phase_list, name='phase-list'),
    path('phases/edit/<int:pk>/', phase_detail, name='phase-detail'),

    # -----------------------------
    # Phase Tasks
    # -----------------------------
    path('tasks/create/', task_create, name='task-create'),
    path('tasks/list/', task_list, name='task-list'),
    path('tasks/edit/<int:pk>/', task_detail, name='task-detail'),

    



    
]
