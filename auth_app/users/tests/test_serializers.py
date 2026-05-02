import pytest
from users.serializers import (
    RegisterSerializer,
    LoginSerializer,
    ProfileDetailSerializer,
    PasswordResetSerializer,
    ActivationKeySerializer
)

@pytest.mark.django_db
class TestRegisterSerializer:
    def test_valid_serializer(self):
        data = {"email": "new@example.com", "password": "test123", "confirm_password": "test123"}
        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid()
        user = serializer.save()
        assert user.email == "new@example.com"
        assert user.check_password("test123")
        assert user.activation_key is not None

    def test_password_mismatch(self):
        data = {"email": "new@example.com", "password": "test123", "confirm_password": "wrong"}
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert "confirm_password" in serializer.errors

    def test_to_representation(self, user):
        serializer = RegisterSerializer(instance=user)
        assert serializer.data == {"user_id": user.id, "email": user.email}

@pytest.mark.django_db
class TestLoginSerializer:
    def test_valid_login(self, user):
        data = {"email": user.email, "password": "password123"}
        serializer = LoginSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data["user"] == user

    def test_user_not_found(self):
        data = {"email": "no@example.com", "password": "password123"}
        serializer = LoginSerializer(data=data)
        assert not serializer.is_valid()
        assert "Пользователь не найден" in str(serializer.errors)

    def test_inactive_user(self, inactive_user):
        data = {"email": inactive_user.email, "password": "password123"}
        serializer = LoginSerializer(data=data)
        assert not serializer.is_valid()
        assert "Пользователь неактивен" in str(serializer.errors)

    def test_wrong_password(self, user):
        data = {"email": user.email, "password": "wrong_password"}
        serializer = LoginSerializer(data=data)
        assert not serializer.is_valid()
        assert "Неверный пароль" in str(serializer.errors)

@pytest.mark.django_db
class TestProfileDetailSerializer:
    def test_serializer_fields(self, user):
        serializer = ProfileDetailSerializer(user)
        assert set(serializer.data.keys()) == {"id", "email", "activation_key", "activation_key_expires"}
        assert serializer.data["id"] == user.id
        assert serializer.data["email"] == user.email
        assert serializer.data["activation_key"] == user.activation_key

@pytest.mark.django_db
class TestPasswordResetSerializer:
    def test_valid_old_password(self, user):
        user.set_password("old_pass")
        user.save()
        serializer = PasswordResetSerializer(
            instance=user,
            data={"old_password": "old_pass", "new_password": "new_pass"}
        )
        assert serializer.is_valid()
        serializer.save()
        user.refresh_from_db()
        assert user.check_password("new_pass")

    def test_invalid_old_password(self, user):
        user.set_password("old_pass")
        user.save()
        serializer = PasswordResetSerializer(
            instance=user,
            data={"old_password": "wrong", "new_password": "new_pass"}
        )
        assert not serializer.is_valid()
        assert "old_password" in serializer.errors

@pytest.mark.django_db
class TestActivationKeySerializer:
    def test_valid_key(self, user):
        data = {"activation_key": user.activation_key}
        serializer = ActivationKeySerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data["user"] == user

    def test_expired_key(self, user_with_expired_key):
        data = {"activation_key": user_with_expired_key.activation_key}
        serializer = ActivationKeySerializer(data=data)
        assert not serializer.is_valid()
        assert "Ключ активации истёк" in str(serializer.errors)

    def test_nonexist_key(self):
        data = {"activation_key": "nonexist"}
        serializer = ActivationKeySerializer(data=data)
        assert not serializer.is_valid()
        assert "Неверный ключ активации" in str(serializer.errors)