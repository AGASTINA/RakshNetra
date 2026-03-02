from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_VIEWER = 'viewer'
    ROLE_OPERATOR = 'operator'
    ROLE_COMMANDER = 'commander'

    ROLE_CHOICES = [
        (ROLE_VIEWER, 'Viewer'),
        (ROLE_OPERATOR, 'Operator'),
        (ROLE_COMMANDER, 'Commander'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_VIEWER)

class AuditLog(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=255)
    ip_address = models.CharField(max_length=50, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.timestamp.isoformat()} - {self.user} - {self.action}"
