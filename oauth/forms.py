from django import forms

from oauth.models import OAuthClient, CallbackUrl


class OAuthClientForm(forms.ModelForm):
    desc = forms.CharField(required=False)

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


class OAuthClientLogoForm(forms.ModelForm):
    class Meta:
        model = OAuthClient
        fields = ('logo',)
