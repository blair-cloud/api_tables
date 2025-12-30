import binascii
import os
from django.db import models
from django.conf import settings


class APIKey(models.Model):
    """
    API Key model for authentication
    """
    key = models.CharField(max_length=40, primary_key=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='api_key',
        on_delete=models.CASCADE
    )
    created = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'API Key'
        verbose_name_plural = 'API Keys'

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    @staticmethod
    def generate_key():
        """Generate a new random API key"""
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return f"API Key for {self.user}"
