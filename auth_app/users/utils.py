from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed


class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        result = super().authenticate(request)

        if result is None:
            return None

        user, token = result

        request.user_id = token.get('user_id')

        if not user.is_active:
            raise AuthenticationFailed("Пользователь неактивен")

        return user, token