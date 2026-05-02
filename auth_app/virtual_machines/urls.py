from django.urls import path

from .views import ActivateKeyAndGetVmView

urlpatterns = [
    path('activate-key/', ActivateKeyAndGetVmView.as_view(), name='activate-key'),
]