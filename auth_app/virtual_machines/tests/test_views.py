from datetime import timedelta

import pytest
from unittest.mock import patch
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from virtual_machines.models import VirtualMachine


@pytest.mark.django_db
class TestActivateKeyAndGetVmView:
    @patch("virtual_machines.views.async_to_sync")
    def test_activate(self, mock_async_to_sync, api_client, user, free_vm):
        VirtualMachine.objects.exclude(id=free_vm.id).delete()
        url = reverse("activate-key")
        data = {"activation_key": user.activation_key}
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {**free_vm.get_data(), "user_id": user.id}
        user.refresh_from_db()
        assert user.activation_key is None
        free_vm.refresh_from_db()
        assert free_vm.current_user_id == user
        assert mock_async_to_sync.called

    def test_activate_no_free_vm(self,  api_client, user):
        VirtualMachine.objects.all().delete()
        url = reverse("activate-key")
        data = {"activation_key": user.activation_key}
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert response.data["detail"] == "Все прокси заняты"
        user.refresh_from_db()
        assert user.activation_key is not None

    def test_activate_invalid_key(self, api_client):
        url = reverse("activate-key")
        data = {"activation_key": "invalidkey"}
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_activate_expired_key(self, api_client, user):
        user.activation_key_expires = timezone.now() - timedelta(days=1)
        user.save()
        url = reverse("activate-key")
        data = {"activation_key": user.activation_key}
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
