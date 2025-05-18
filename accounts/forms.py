from distutils.command.clean import clean

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm as _AuthenticationForm
from django.contrib.auth.forms import UserCreationForm as _UserCreationForm
from django.forms import ValidationError

User = get_user_model()
class UserCreationForm(_UserCreationForm):
    error_messages = {
        **_UserCreationForm.error_messages,
        'duplicate_email': 'Email in use',
    }

    class Meta(_UserCreationForm.Meta):
        model = User
        fields = ('email',)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError(self.error_messages['duplicate_email'], code='duplicate_email')
        return email


class AuthenticationForm(_AuthenticationForm):
    def clean(self):
        cleaned_data = super().clean()
        if not self.user_cache.is_verified:
            raise ValidationError('user is not verified', code='not_verified')

        return cleaned_data


class SendVerificationForm(forms.Form):
    username = forms.EmailField()

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user = None

    def clean_username(self):
        email = self.cleaned_data.get('username')
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            raise ValidationError('not an issued email', code='not_found')

        self.user = user
        return self.cleaned_data
