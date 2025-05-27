from django import forms

from oauth.models import OAuthClient, CallbackUrl


class OAuthClientForm(forms.ModelForm):
    class Meta:
        model = OAuthClient
        fields = ('name', 'desc',)


class OAuthEntrypointForm(forms.ModelForm):
    class Meta:
        model = OAuthClient
        fields = ('entrypoint',)


class CallbackUrlForm(forms.ModelForm):
    class Meta:
        model = CallbackUrl
        fields = ('url',)
