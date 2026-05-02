import pytest
from rest_framework.test import APIClient
from django.utils import timezone

from users.models import User
from virtual_machines.models import VirtualMachine

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user():
    return User.objects.create_user(email="test@example.com", password="pass")

@pytest.fixture
def free_vm():
    return VirtualMachine.objects.create(
        name="free-proxy",
        host="192.168.1.1",
        port=1080,
        protocol="socks5",
        is_active=True,
        current_user_id=None,
        last_used_at=None
    )

@pytest.fixture
def busy_vm(user):
    return VirtualMachine.objects.create(
        name="busy-proxy",
        host="192.168.1.2",
        port=8080,
        protocol="http",
        is_active=True,
        current_user_id=user,
        last_used_at=timezone.now()
    )