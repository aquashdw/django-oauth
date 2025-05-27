from django.db import models

from oauth.models import OAuthClient


class Review(models.Model):
    client = models.ForeignKey(OAuthClient, on_delete=models.CASCADE)
    reason = models.TextField()
    decision = models.CharField(max_length=8, choices=[
        (OAuthClient.PRODUCTION, 'Production'),
        (OAuthClient.REJECTED, 'Rejected'),
    ], null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
