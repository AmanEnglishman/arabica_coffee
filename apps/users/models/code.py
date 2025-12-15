import random
import string
from datetime import timedelta
from django.utils import timezone
from django.db import models

class PhoneConfirmationCode(models.Model):
    phone_number = models.CharField(max_length=20)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["phone_number", "code"]),
        ]

    def is_expired(self):
        return self.created_at < timezone.now() - timedelta(minutes=5)

    @staticmethod
    def generate_code():
        return ''.join(random.choices(string.digits, k=6))
