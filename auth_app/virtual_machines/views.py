from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from users.serializers import ActivationKeySerializer
from users.services import delete_activation_key_user
from .services import connect_user_to_vm


class ActivateKeyAndGetVmView(APIView):

    @extend_schema(
        summary="Активация по ключу и получение прокси",
        description="Принимает ключ активации. При успехе активирует пользователя, назначает свободную ВМ и возвращает её параметры.",
        request=ActivationKeySerializer,
        responses={
            200: OpenApiResponse(
                description="Прокси выдан",
                response={
                    "type": "object",
                    "properties": {
                        "host": {"type": "string"},
                        "port": {"type": "integer"},
                        "protocol": {"type": "string", "enum": ["socks5", "http", "https"]},
                        "user_id": {"type": "integer"}
                    }
                }
            ),
            400: OpenApiResponse(description="Ошибка валидации"),
            503: OpenApiResponse(description="Нет свободных прокси", ),
        },
    )
    def post(self, request):
        serializer = ActivationKeySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        group_user_name = f"user_{user.id}"
        send_data = {
            'type': 'send_status',
            'status': 'connecting',
            'message': 'Подключение к серверу'
        }

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(group_user_name, send_data)

        vm_data = connect_user_to_vm(user)
        send_data['status'] = 'no_free_vms'
        send_data['message'] = 'Все прокси заняты'
        if not vm_data:
            async_to_sync(channel_layer.group_send)(group_user_name, send_data)
            return Response({"detail": "Все прокси заняты"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        delete_activation_key_user(user)
        send_data['status'] = 'connected'
        send_data['message'] = 'Подключено к виртуальной машине'
        async_to_sync(channel_layer.group_send)(group_user_name, send_data)
        return Response({**vm_data, 'user_id': user.id}, status=status.HTTP_200_OK)
