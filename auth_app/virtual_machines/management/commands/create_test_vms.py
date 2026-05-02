from django.core.management.base import BaseCommand
from virtual_machines.models import VirtualMachine

class Command(BaseCommand):
    def handle(self, *args, **options):
        vms_data = [
            {'name': 'proxy-1', 'host': '192.168.1.10', 'port': 1080, 'protocol': 'socks5'},
            {'name': 'proxy-2', 'host': '192.168.1.11', 'port': 8080, 'protocol': 'http'},
            {'name': 'proxy-3', 'host': '192.168.1.12', 'port': 443, 'protocol': 'https'},
        ]

        for data in vms_data:
            VirtualMachine.objects.get_or_create(
                name=data['name'],
                defaults={
                    'host': data['host'],
                    'port': data['port'],
                    'protocol': data['protocol'],
                    'is_active': True,
                    'current_user_id': None,
                    'last_used_at': None,
                }
            )
