import pytest
from virtual_machines.models import VirtualMachine

@pytest.mark.django_db
class TestVirtualMachineModel:
    def test_str_representation(self, free_vm):
        expected = f"{free_vm.name} ({free_vm.host}:{free_vm.port})"
        assert str(free_vm) == expected

    def test_get_data(self, free_vm):
        data = free_vm.get_data()
        assert data == {
            'host': free_vm.host,
            'port': free_vm.port,
            'protocol': free_vm.protocol
        }

    def test_default_values(self):
        vm = VirtualMachine.objects.create(
            name="default-test",
            host="10.0.0.1",
            port=3128,
            protocol="http"
        )
        assert vm.is_active is True
        assert vm.current_user_id is None
        assert vm.last_used_at is None