from django.urls import path
from .views import (

    # Project
    PhaseTaskViewSet,
    ProjectFullDetailAPIView,
    ProjectPhaseViewSet,
    ProjectViewSet,
    ProjectTypeFilterView,

)


# ---------`--------------------
# Project ViewSet mappings
# -----------------------------
project_create = ProjectViewSet.as_view({"post": "create"})
project_list = ProjectViewSet.as_view({"get": "list"})
project_edit = ProjectViewSet.as_view({"patch": "partial_update"})
project_delete = ProjectViewSet.as_view({"delete": "destroy"})

# -----------------------------
# Phase ViewSet mappings
# -----------------------------
phase_create = ProjectPhaseViewSet.as_view({"post": "create"})
phase_list = ProjectPhaseViewSet.as_view({"get": "list"})
phase_edit = ProjectPhaseViewSet.as_view({"patch": "partial_update",})
phase_delete = ProjectPhaseViewSet.as_view({"delete": "destroy",})

# -----------------------------
# Task ViewSet mappings
# -----------------------------
task_create = PhaseTaskViewSet.as_view({"post": "create"})
task_list = PhaseTaskViewSet.as_view({"get": "list"})
task_edit = PhaseTaskViewSet.as_view({"patch": "partial_update",})
task_delete = PhaseTaskViewSet.as_view({"delete": "destroy",})



urlpatterns = [

    # -----------------------------
    # Projects
    # -----------------------------
    path('projects/create/', project_create, name='project-create'),
    path('projects/list/', project_list, name='project-list'),
    path('projects/edit/<str:project_id>/', project_edit, name='project-edit'),
    path('projects/delete/<str:project_id>/', project_delete, name='project-delete'),
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
    path('phases/edit/<str:project_id>/',phase_edit,name='phase-edit'),
    path('phases/delete/<str:project_id>/',phase_delete,name='phase-delete'),
    path("projects/phases/<str:project_id>/",ProjectPhaseViewSet.as_view({"get": "list"}),),

    # -----------------------------
    # Phase Tasks
    # -----------------------------
    path('tasks/create/', task_create, name='task-create'),
    path('tasks/list/', task_list, name='task-list'),
    path('tasks/edit/<int:pk>/', task_edit, name='task-edit'),
    path('tasks/delete/<int:pk>/', task_delete, name='task-delete'),

    
]
