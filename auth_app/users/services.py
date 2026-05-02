import secrets
from dataclasses import dataclass
from datetime import timedelta

from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User


@dataclass(frozen=True)
class TokenPare:
    access_token: str
    refresh_token: str


def get_token_pare_for_user(user: User) -> TokenPare:
    """Возвращает объект TokenPare с access и refresh токенами"""
    refresh = RefreshToken.for_user(user)

    return TokenPare(
        access_token=str(refresh.access_token),
        refresh_token=str(refresh),
    )

def update_activation_key_user(user: User) -> User:
    """Обновляет ключ активации"""
    user.activation_key = secrets.token_hex(16)
    user.activation_key_expires = timezone.now() + timedelta(days=1)
    user.save()
    return user

def delete_activation_key_user(user: User) -> User:
    """Удаляет ключ активации"""
    user.activation_key = None
    user.activation_key_expires = None
    user.save()
    return user
