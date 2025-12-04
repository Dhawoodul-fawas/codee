from django.urls import path
from .views import ApkLoginView

urlpatterns = [
    path("login/", ApkLoginView.as_view()),
]
