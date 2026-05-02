from django.db import models

from core.settings import AUTH_USER_MODEL


class VirtualMachine(models.Model):
    PROTOCOL_CHOICES = [
        ('socks5', 'SOCKS5'),
        ('http', 'HTTP'),
        ('https', 'HTTPS'),
    ]

    name = models.CharField(max_length=100)
    host = models.CharField(max_length=255)
    port = models.IntegerField()
    protocol = models.CharField(max_length=10, choices=PROTOCOL_CHOICES)
    is_active = models.BooleanField(default=True)
    current_user_id = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    last_used_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.host}:{self.port})"

    def get_data(self):
        return {
            'host': self.host,
            'port': self.port,
            'protocol': self.protocol,
        }
