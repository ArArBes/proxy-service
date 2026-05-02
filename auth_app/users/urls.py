from django.urls import path

from .views import (
    RegisterView,
    LoginView,
    ProfileView,
    PasswordResetView,
    RefreshActivationKeyView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('change-password/', PasswordResetView.as_view(), name='change-password'),
    path('refresh-key/', RefreshActivationKeyView.as_view(), name='refresh-key'),
]
