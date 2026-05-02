import pytest
from channels.routing import URLRouter
from django.urls import re_path
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer

from virtual_machines.consumers import VMConnect
from virtual_machines.models import VirtualMachine
from users.models import User

application = URLRouter([
    re_path(r'ws/status/(?P<user_id>\d+)/$', VMConnect.as_asgi()),
])

@database_sync_to_async
def create_user_and_vm():
    user = User.objects.create_user(email="ws@example.com", password="pass")
    vm = VirtualMachine.objects.create(
        name="test-vm",
        host="10.0.0.1",
        port=1080,
        protocol="socks5",
        is_active=True,
        current_user_id=user
    )
    return user, vm

@database_sync_to_async
def get_vm_current_user_id(vm_id):
    return VirtualMachine.objects.filter(id=vm_id).first().current_user_id

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_websocket():
    user, vm = await create_user_and_vm()
    communicator = WebsocketCommunicator(application, f"/ws/status/{user.id}/")
    connected, _ = await communicator.connect()
    assert connected
    response = await communicator.receive_json_from()
    assert response["status"] == "connected"
    await communicator.send_json_to({"action": "disconnect"})
    closed = await communicator.receive_output()
    assert closed["type"] == "websocket.close"
    current_user = await get_vm_current_user_id(vm.id)
    assert current_user is None

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_websocket_send_status():
    user = await database_sync_to_async(User.objects.create_user)(
        email="ws2@example.com", password="pass"
    )
    communicator = WebsocketCommunicator(application, f"/ws/status/{user.id}/")
    await communicator.connect()

    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        f"user_{user.id}",
        {
            "type": "send_status",
            "status": "connected",
            "message": "OK"
        }
    )
    response = await communicator.receive_json_from()
    assert response["status"] == "connected"
    assert response["message"] == "OK"
    await communicator.disconnect()