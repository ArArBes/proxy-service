import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from datetime import timedelta
from django.utils import timezone

@pytest.fixture
def User():
    return get_user_model()

@pytest.fixture
def user(User):
    return User.objects.create_user(
        email="test@example.com",
        password="password123"
    )

@pytest.fixture
def inactive_user(User):
    user = User.objects.create_user(email="inactive@example.com", password="password123")
    user.is_active = False
    user.save()
    return user

@pytest.fixture
def user_with_expired_key(User):
    user = User.objects.create_user(email="expired@example.com", password="password123")
    user.activation_key_expires = timezone.now() - timedelta(days=1)
    user.save()
    return user

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client