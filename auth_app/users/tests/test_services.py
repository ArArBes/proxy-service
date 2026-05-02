import pytest
from datetime import timedelta
from django.utils import timezone
from users.services import get_token_pare_for_user, update_activation_key_user, delete_activation_key_user


@pytest.mark.django_db
class TestTokenPair:
    def test_get_token_pare(self, user):
        tokens = get_token_pare_for_user(user)
        assert tokens.access_token
        assert tokens.refresh_token
        assert isinstance(tokens.access_token, str)
        assert isinstance(tokens.refresh_token, str)

        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken(tokens.refresh_token)
        assert str(refresh.access_token) != tokens.access_token


@pytest.mark.django_db
class TestUpdateActivationKey:
    def test_update_activation_key(self, user):
        old_key = user.activation_key
        old_expiry = user.activation_key_expires
        updated_user = update_activation_key_user(user)
        assert updated_user == user
        assert user.activation_key != old_key
        assert user.activation_key is not None
        assert len(user.activation_key) == 32
        assert user.activation_key_expires is not None
        assert user.activation_key_expires > timezone.now() - timedelta(seconds=1)
        assert user.activation_key_expires > old_expiry if old_expiry else True


@pytest.mark.django_db
class TestDeleteActivationKey:
    def test_delete_activation_key(self, user):
        assert user.activation_key is not None
        assert user.activation_key_expires is not None
        delete_activation_key_user(user)
        assert user.activation_key is None
        assert user.activation_key_expires is None
