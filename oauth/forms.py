from django import forms

from oauth.models import OAuthClient, CallbackUrl


class OAuthClientForm(forms.ModelForm):
    class Meta:
        model = OAuthClient
        fields = ('name',)


class CallbackUrlForm(forms.ModelForm):
    class Meta:
        model = CallbackUrl
        fields = ('url',)
