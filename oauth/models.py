from django.conf import settings
from django.db import models


class OAuthClient(models.Model):
    DEVELOPMENT = 'DEV'
    PRODUCTION = 'PROD'
    DELETED = 'DEL'
    STATUS_CHOICES = [
        (DEVELOPMENT, 'Development'),
        (PRODUCTION, 'Production'),
        (DELETED, 'Deleted'),
    ]

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    client_id = models.CharField(max_length=128)
    client_secret = models.CharField(max_length=128)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default=DEVELOPMENT)

    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='using_apps')
    test_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='is_tester_of')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        permissions = [
            ('oauth_active', 'Can use oauth features'),
        ]


class CallbackUrl(models.Model):
    client = models.ForeignKey(OAuthClient, on_delete=models.CASCADE, related_name='callback_urls')
    url = models.URLField(max_length=256)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['client', 'url'], name='unique_url_per_client')
        ]
