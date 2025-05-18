from django.conf import settings
from django.db import models


class OAuthClient(models.Model):
    DEVELOPMENT = 'DEV'
    PRODUCTION = 'PROD'
    STATUS_CHOICES = [
        (DEVELOPMENT, 'Development'),
        (PRODUCTION, 'Production'),
    ]

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    client_id = models.CharField(max_length=128)
    client_secret = models.CharField(max_length=128)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default=DEVELOPMENT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class CallbackUrl(models.Model):
    client = models.ForeignKey(OAuthClient, on_delete=models.CASCADE)
    url = models.URLField(max_length=256)
