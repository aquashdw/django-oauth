from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.forms import ValidationError

User = get_user_model()
class CustomUserCreationForm(UserCreationForm):
    error_messages = {
        **UserCreationForm.error_messages,
        'duplicate_email': 'Email in use',
    }

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email',)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError(self.error_messages['duplicate_email'], code='duplicate_email')
        return email
