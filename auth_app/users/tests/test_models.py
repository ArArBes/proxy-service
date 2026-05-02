import pytest
from datetime import timedelta
from django.utils import timezone


@pytest.mark.django_db
class TestUserManager:
    def test_create_user_without_email(self, User):
        with pytest.raises(ValueError, match="Users must have an email address"):
            User.objects.create_user(email=None, password="pass")

    def test_create_user(self, User):
        user = User.objects.create_user(email="test@example.com", password="password")
        assert user.email == "test@example.com"
        assert user.check_password("password")
        assert user.activation_key is not None
        assert len(user.activation_key) == 32
        assert user.activation_key_expires > timezone.now()
        assert user.is_active

    def test_create_superuser(self, User):
        user = User.objects.create_superuser(email="admin@example.com", password="admin")
        assert user.is_superuser
        assert user.is_staff
        assert user.is_active

@pytest.mark.django_db
class TestUserModel:
    def test_is_activation_key_valid_with_valid_key(self, user):
        assert user.is_activation_key_valid(user.activation_key) is True

    def test_is_activation_key_valid_expired(self, user):
        user.activation_key_expires = timezone.now() - timedelta(days=1)
        user.save()
        assert user.is_activation_key_valid(user.activation_key) is False

    def test_is_activation_key_valid_no_expiry(self, user):
        user.activation_key_expires = None
        user.save()
        assert user.is_activation_key_valid(user.activation_key) is True

    def test_is_activation_key_valid_wrong_key(self, user):
        assert user.is_activation_key_valid("wrongkey") is False