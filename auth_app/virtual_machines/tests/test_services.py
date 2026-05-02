import pytest

from virtual_machines.models import VirtualMachine
from virtual_machines.services import connect_user_to_vm

@pytest.mark.django_db
class TestConnectUserToVm:
    def test_connect_to_free_vm(self, user, free_vm):
        VirtualMachine.objects.exclude(id=free_vm.id).delete()
        result = connect_user_to_vm(user)
        assert result is not None
        assert result == free_vm.get_data()
        free_vm.refresh_from_db()
        assert free_vm.current_user_id == user
        assert free_vm.last_used_at is not None

    def test_no_free_vm(self, user, busy_vm):
        VirtualMachine.objects.exclude(id=busy_vm.id).delete()
        result = connect_user_to_vm(user)
        assert result is None
        busy_vm.refresh_from_db()
        assert busy_vm.current_user_id is not None

    def test_inactive_vm(self, user):
        VirtualMachine.objects.all().delete()
        inactive_vm = VirtualMachine.objects.create(
            name="inactive",
            host="1.1.1.1",
            port=1111,
            protocol="http",
            is_active=False
        )
        result = connect_user_to_vm(user)
        assert result is None
        inactive_vm.refresh_from_db()
        assert inactive_vm.current_user_id is None