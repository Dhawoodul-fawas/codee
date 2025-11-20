from django.urls import path
from .views import LoginView, RegisterListView, RegisterView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('register-list/', RegisterListView.as_view(), name='register_list'),

    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]
