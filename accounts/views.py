from urllib.parse import urlencode
from uuid import uuid4

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_safe

from accounts.forms import UserCreationForm, AuthenticationForm, SendVerificationForm
from accounts.rabbit import send_mail
from django_oauth.utils import anonymous, extract_form_errors, redirect_with_nq


def index(request):
    return render(request, 'accounts/index.html')


@anonymous
def signup(request):
    if request.method == 'POST':
        params = {}
        if request.GET.get('next'):
            params['next'] = request.GET.get('next')

        form = UserCreationForm(request.POST)
        if form.is_valid():
            instance = form.save()
            uuid = str(uuid4()).replace('-', '')
            signup_token = f'auth-signup-token-{uuid}'
            params['token'] = uuid
            link = f'{reverse("accounts:signup_confirm")}?{urlencode(params)}'
            send_mail(instance.email, 'Sign Up Request', f'<a href="{link}">Sign Up Link</a>')

            cache.set(signup_token, instance, timeout=600)

            return redirect_with_nq('accounts:verify', {'created': 'true'})

        params['errors'] = ','.join(extract_form_errors(form))
        params['email'] = form.data.get('email')
        return redirect_with_nq('accounts:signup', params)

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
    if not instance:
        raise Http404
    instance.is_verified = True
    instance.save()
    cache.delete(signup_token)
    params = {
        'created': 'true',
    }
    if request.GET.get('next'):
        params['next'] = request.GET.get('next')

    return redirect_with_nq('accounts:signin', params)


@anonymous
def signin(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        next_url = request.GET.get('next')
        if form.is_valid():
            login(request, form.get_user())
            return redirect(next_url if next_url is not None else 'accounts:index')

        params = {}
        if next_url:
            params['next'] = next_url

        errors = extract_form_errors(form)
        if 'not_verified' in errors:
            params['email'] = form.get_user().email
            return redirect_with_nq('accounts:verify', params)

        params['errors'] = ','.join(errors)
        return redirect_with_nq('accounts:signin', params)

    context = {
        'errors': request.GET.get('errors', '').split(','),
    }
    if request.GET.get('created') == 'true':
        context['created'] = True
    return render(request, 'accounts/signin.html', context)


@login_required
def signout(request):
    if request.method == 'POST':
        logout(request)
    return redirect('accounts:index')


@login_required
def my_profile(request):
    return render(request, 'accounts/my-profile.html')


@anonymous
def verify_request(request):
    if request.method == 'POST':
        form = SendVerificationForm(request.POST)
        if form.is_valid():
            user = form.user
            uuid = str(uuid4()).replace('-', '')
            signup_token = f'auth-signup-token-{uuid}'
            params = {
                'token': uuid
            }
            link = f'{reverse("accounts:signup_confirm")}?{urlencode(params)}'
            send_mail(user.email, 'Sign Up Request', f'<a href="{link}">Sign Up Link</a>')

            cache.set(signup_token, user, timeout=600)

            return redirect_with_nq('accounts:verify', {'resent': 'true', 'email': user.email})

        return redirect('/400')

    context = {}
    if request.GET.get('created') == 'true':
        context['created'] = True
    if request.GET.get('resent') == 'true':
        context['resent'] = True
    context['email'] = request.GET.get('email')

    return render(request, 'accounts/verify.html', context)
