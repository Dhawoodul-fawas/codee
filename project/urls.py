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
    # Create & List
    path('projects/create/', project_create, name='project-create'),
    path('projects-list/', project_list, name='project-list'),

    # Detail / Update / Delete
    path('projects/edit/<int:pk>/', project_detail, name='project-detail'),

    # Filters
    path('projects/filter/status/<str:status>/', ProjectStatusFilterView.as_view(), name='project-filter-status'),
    path('projects/filter/type/<str:ptype>/', ProjectTypeFilterView.as_view(), name='project-filter-type'),
]
