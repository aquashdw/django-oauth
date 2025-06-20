from django.conf import settings
from django.db import models


def set_logo_path(instance, _):
    return f'client/{instance.pk}/logo.png'


class OAuthClient(models.Model):
    DEVELOPMENT = 'DEV'
    PRODUCTION = 'PROD'
    REVIEWING = 'REV'
    REJECTED = 'REJ'
    CLOSED = 'CLO'
    DELETED = 'DEL'
    STATUS_CHOICES = [
        (DEVELOPMENT, 'Development'),
        (PRODUCTION, 'Production'),
        (REVIEWING, 'Under Review'),
        (REJECTED, 'Rejected'),
        (CLOSED, 'Closed'),
        (DELETED, 'Deleted'),
    ]

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='client_apps')
    logo = models.ImageField(max_length=256, null=True, upload_to=set_logo_path)
    name = models.CharField(max_length=128)
    desc = models.CharField(max_length=128, null=True)
    entrypoint = models.URLField(max_length=256, null=True)
    client_id = models.CharField(max_length=128)
    client_secret = models.CharField(max_length=128)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default=DEVELOPMENT)

    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='using_apps')
    test_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='is_tester_of')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_desc(self):
        return self.desc if self.desc else ''

    def get_entry(self):
        return self.entrypoint if self.entrypoint else ''

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
