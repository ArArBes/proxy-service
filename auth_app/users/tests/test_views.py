import pytest
from unittest.mock import patch
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestRegisterView:
    @patch("users.views.send_activation_key.delay")
    def test_register(self, mock_send, api_client, User):
        url = reverse("register")
        data = {
            "email": "newuser@example.com",
            "password": "123",
            "confirm_password": "123",
        }
        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert "access_token" in response.data
        assert "refresh_token" in response.data
        mock_send.assert_called_once()
        user = User.objects.get(email="newuser@example.com")
        assert user is not None
        assert user.activation_key is not None

    def test_register_password(self, api_client):
        url = reverse("register")
        data = {
            "email": "test@example.com",
            "password": "123",
            "confirm_password": "different",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "confirm_password" in response.data

    def test_register_existing_email(self, api_client, user):
        url = reverse("register")
        data = {
            "email": user.email,
            "password": "123",
            "confirm_password": "123",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLoginView:
    def test_login(self, api_client, user):
        user.set_password("1234")
        user.save()
        url = reverse("login")
        data = {"email": user.email, "password": "1234"}
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.data
        assert "refresh_token" in response.data

    def test_login_wrong_password(self, api_client, user):
        url = reverse("login")
        data = {"email": user.email, "password": "wrong"}
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_inactive_user(self, api_client, inactive_user):
        url = reverse("login")
        data = {"email": inactive_user.email, "password": "pass"}
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Пользователь неактивен" in str(response.data)

    def test_user_not_found(self, api_client):
        url = reverse("login")
        data = {"email": "check@example.com", "password": "pass"}
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestProfileView:
    def test_get_profile_authenticated(self, authenticated_client, user):
        url = reverse("profile")
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == user.email
        assert "activation_key" in response.data

    def test_get_profile_unauthenticated(self, api_client):
        url = reverse("profile")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestPasswordResetView:
    def test_change_password(self, authenticated_client, user):
        user.set_password("old_pass")
        user.save()
        url = reverse("change-password")
        data = {"old_password": "old_pass", "new_password": "new_pass"}
        response = authenticated_client.patch(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.check_password("new_pass")

    def test_change_password_wrong_old(self, authenticated_client, user):
        user.set_password("old_pass")
        user.save()
        url = reverse("change-password")
        data = {"old_password": "wrong", "new_password": "new_pass"}
        response = authenticated_client.patch(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "old_password" in response.data

    def test_change_password_unauthenticated(self, api_client):
        url = reverse("change-password")
        data = {"old_password": "old", "new_password": "new"}
        response = api_client.patch(url, data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestRefreshActivationKeyView:
    @patch("users.views.send_activation_key.delay")
    def test_refresh_key(self, mock_send, authenticated_client, user):
        old_key = user.activation_key
        url = reverse("refresh-key")
        response = authenticated_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        assert "activation_key" in response.data
        assert response.data["activation_key"] != old_key
        user.refresh_from_db()
        assert user.activation_key == response.data["activation_key"]
        mock_send.assert_called_once_with(user.email, user.activation_key)

    def test_refresh_key_unauthenticated(self, api_client):
        url = reverse("refresh-key")
        response = api_client.post(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED