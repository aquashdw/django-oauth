from urllib.parse import urlencode
from uuid import uuid4

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_safe

from accounts.forms import UserCreationForm, AuthenticationForm
from accounts.rabbit import send_mail
from accounts.utils import anonymous, extract_form_errors


def index(request):
    return render(request, 'accounts/index.html')


@anonymous
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            instance = form.save()
            uuid = str(uuid4()).replace('-', '')
            signup_token = f'auth-signup-token-{uuid}'
            link = f'{reverse("accounts:signup_confirm")}?{urlencode({"token": uuid})}'
            send_mail(instance.email, 'Sign Up Request', f'<a href="{link}">Sign Up Link</a>')
            
            cache.set(signup_token, instance, timeout=600)

            return redirect(f'{reverse("accounts:index")}?{urlencode({"success": "true"})}')

        errors = ','.join(extract_form_errors(form))
        email = form.data.get('email')
        params = {
            'errors': errors,
            'email': email,
        }
        return redirect(f'{reverse("accounts:signup")}?{urlencode(params)}')

    context = {
        'errors': request.GET.get('errors', '').split(','),
        'email': request.GET.get('email', None),
    }
    
    return render(request, 'accounts/signup.html', context)


@require_safe
def signup_confirm(request):
    token = request.GET.get('token')
    if not token:
        return redirect('accounts:signin')
    
    signup_token = f'auth-signup-token-{token}'
    instance = cache.get(signup_token)
    instance.is_verified = True
    instance.save()
    cache.delete(signup_token)

    return redirect(f'{reverse("accounts:index")}?{urlencode({"created": "true"})}')



@anonymous
def signin(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('accounts:index')
        errors = ','.join(extract_form_errors(form))
        params = {
            'errors': errors,
        }
        return redirect(f'{reverse("accounts:signin")}?{urlencode(params)}')
    return render(request, 'accounts/signin.html')


@login_required
def signout(request):
    if request.method == 'POST':
        logout(request)
    return redirect('accounts:index')


@login_required
def my_profile(request):
    return render(request, 'accounts/my-profile.html')