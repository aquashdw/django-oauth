from urllib.parse import urlencode
from uuid import uuid4

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.cache import cache
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_safe

from accounts.forms import CustomUserCreationForm
from accounts.rabbit import send_mail
from accounts.utils import require_anonymous


def index(request):
    return render(request, 'accounts/index.html')


@require_anonymous
def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.is_active = False
            instance.save()
            uuid = str(uuid4()).replace('-', '')
            signup_token = f'auth-signup-token-{uuid}'
            link = f'{reverse("accounts:signup_confirm")}?{urlencode({"token": uuid})}'
            send_mail(instance.email, 'Sign Up Request', f'<a href="{link}">Sign Up Link</a>')
            
            cache.set(signup_token, instance, timeout=600)

            return redirect(f'{reverse("accounts:index")}?{urlencode({"success": "true"})}')
        
        base_url = reverse('accounts:signup')
        errors = []
        error_data = form.errors.as_data()
        for error_param in error_data:
            param_errors = error_data[error_param]
            for error in param_errors:
                errors.append(error.code)         

        errors = ','.join(errors)
        email = form.data.get('email')
        params = {
            'errors': errors,
            'email': email,
        }
        params = urlencode(params)
        return redirect(f'{base_url}?{params}')

    context = {
        'errors': request.GET.get('errors', '').split(','),
        'email': request.GET.get('email', None),
    }
    
    return render(request, 'accounts/signup.html', context)


@require_safe
def signup_confirm(request):

    token = request.GET.get('token')
    if not token:
        return redirect('accounts:login')
    
    signup_token = f'auth-signup-token-{token}'
    instance = cache.get(signup_token)
    instance.is_active = True
    instance.save()
    cache.delete(signup_token)

    return redirect(f'{reverse("accounts:index")}?{urlencode({"success": "true"})}')



@require_anonymous
def signin(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('accounts:index')

        return redirect('accounts:login')
    return render(request, 'accounts/signin.html')
