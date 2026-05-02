import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class VMConnect(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.group_name = f'user_{self.user_id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send(text_data=json.dumps({'status': 'connected', 'message': 'OK'}))

    async def disconnect(self, close_code):
        await self._release_vm()
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get('action') == 'disconnect':
            await self._release_vm()
            await self.close()

    async def _release_vm(self):
        from virtual_machines.models import VirtualMachine
        vm = await database_sync_to_async(
            VirtualMachine.objects.filter(current_user_id=self.user_id).first
        )()
        if vm:
            vm.current_user_id = None
            vm.last_used_at = None
            await database_sync_to_async(vm.save)()

    async def send_status(self, event):
        await self.send(text_data=json.dumps({
            'status': event['status'],
            'message': event['message'],
            'data': event.get('data')
        }))