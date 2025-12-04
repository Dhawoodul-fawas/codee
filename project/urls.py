from django.urls import path
from .views import (
    ProjectViewSet,
    ProjectStatusFilterView,
    ProjectTypeFilterView
)

project_create = ProjectViewSet.as_view({
    "post": "create"
})

project_list = ProjectViewSet.as_view({
    "get": "list"
})

project_detail = ProjectViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy"
})

urlpatterns = [
    # Create & List & Detail (same style as employee URLs)
    path('project/', project_create, name='project_create'),
    path('project-list/', project_list, name='project_list'),
    path('project/<int:pk>/', project_detail, name='project_detail'),

    # Filter by status
    path('projects/status/<str:status>/', ProjectStatusFilterView.as_view(), name='project_status_filter'),

    # Filter by type
    path('projects/type/<str:ptype>/', ProjectTypeFilterView.as_view(), name='project_type_filter'),
]
