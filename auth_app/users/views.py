from rest_framework import status
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .serializers import RegisterSerializer, LoginSerializer, ProfileDetailSerializer, PasswordResetSerializer
from .permissions import IsAuthenticatedUser
from .tasks import send_activation_key
from .services import get_token_pare_for_user, update_activation_key_user


class RegisterView(APIView):
    serializer_class = RegisterSerializer

    @extend_schema(
        summary="Регистрация пользователя",
        description="Принимает email, пароль, подтверждение пароля. Создаёт нового пользователя.",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'email': {'type': 'string', 'format': 'email'},
                    'password': {'type': 'string', 'format': 'password'},
                    'confirm_password': {'type': 'string', 'format': 'password'},
                },
                'required': ['email', 'password', 'confirm_password'],
            }
        },
        responses={
            201: OpenApiResponse(description='Пользователь создан'),
            400: OpenApiResponse(description='Ошибка валидации'),
        }
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_activation_key.delay(user.email, user.activation_key)
            tokens = get_token_pare_for_user(user)
            return Response(
                {
                    "access_token": tokens.access_token,
                    "refresh_token": tokens.refresh_token
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    serializer_class = LoginSerializer

    @extend_schema(
        summary="Аутентификация пользователя",
        description="Принимает логин и пароль",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'email': {'type': 'string', 'format': 'email'},
                    'password': {'type': 'string', 'format': 'password'}
                },
                'required': ['email', 'password'],
            }
        },
        responses={
            200: OpenApiResponse(description='Пользователь аутентифицирован'),
            400: OpenApiResponse(description='Ошибка валидации'),
        }
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.validated_data['user']
        tokens = get_token_pare_for_user(user)
        return Response(
            {
                "access_token": tokens.access_token,
                "refresh_token": tokens.refresh_token
            },
            status=status.HTTP_200_OK)


class ProfileView(APIView):
    serializer_class = ProfileDetailSerializer
    permission_classes = [IsAuthenticatedUser]

    @extend_schema(
        summary="Профиль пользователя",
        description="Возвращает email, ключ активации и срок его действия.",
        responses={
            200: OpenApiResponse(description="Данные профиля", response=ProfileDetailSerializer),
            401: OpenApiResponse(description="Не авторизован"),
        },
        auth=[]
    )
    def get(self, request):
        serializer = ProfileDetailSerializer(request.user)
        return Response(serializer.data)


@extend_schema(
    summary="Смена пароля",
    description="Принимает старый и новый пароль.",
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'old_password': {'type': 'string'},
                'new_password': {'type': 'string'},
            },
            'required': ['old_password', 'new_password'],
        }
    },
    responses={
        200: OpenApiResponse(description="Пароль изменён"),
        400: OpenApiResponse(description="Ошибка валидации"),
        401: OpenApiResponse(description="Не авторизован"),
    },
    auth=[]
)
class PasswordResetView(UpdateAPIView):
    serializer_class = PasswordResetSerializer
    permission_classes = [IsAuthenticatedUser]

    def get_object(self):
        return self.request.user


class RefreshActivationKeyView(APIView):
    permission_classes = [IsAuthenticatedUser]

    @extend_schema(
        summary="Обновить ключ активации",
        description="Генерирует новый ключ, отправляет на email и возвращает его.",
        responses={
            200: OpenApiResponse(
                description="Новый ключ",
                response={
                    'type': 'object',
                    'properties': {'activation_key': {'type': 'string'}}
                }
            ),
            401: OpenApiResponse(description="Не авторизован"),
        },
        auth=[]
    )
    def post(self, request):
        user = request.user
        update_activation_key_user(user)
        send_activation_key.delay(user.email, user.activation_key)
        return Response({'activation_key': user.activation_key}, status=status.HTTP_200_OK)
