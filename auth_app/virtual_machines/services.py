from typing import Optional, Dict

from django.utils import timezone

from .models import VirtualMachine
from users.models import User


def connect_user_to_vm(user: User) -> Optional[Dict[str, str | int]]:
    """
    Принимает id пользователя, ищет свободные вм.
    При нахождении соединяет пользователя и вм.
    """
    free_vm = VirtualMachine.objects.filter(current_user_id=None, is_active=True).first()
    if not free_vm:
        return None

    free_vm.current_user_id = user
    free_vm.last_used_at = timezone.now()
    free_vm.save()

    return free_vm.get_data()
