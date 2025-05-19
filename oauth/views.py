from django.contrib.auth.decorators import permission_required, login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from django_oauth.utils import get_perm

OAUTH_CODENAME = 'oauth_active'
OAUTH_LOOKUP_NAME = 'oauth.oauth_active'

# activate
@login_required
def activate(request):
    if request.user.has_perm(OAUTH_LOOKUP_NAME):
        return redirect('oauth:index')

    if request.method == 'POST':
        request.user.user_permissions.add(get_perm(OAUTH_CODENAME))
        request.user.save()
        return redirect('oauth:index')

    return render(request, 'oauth/activate.html')


# dashboard (read clients)
@permission_required(OAUTH_LOOKUP_NAME, login_url='oauth:activate')
def index(request):
    return render(request, 'oauth/index.html')


# create client
def create_client(request):
    pass


# read one client
def read_client(request):
    pass


# update client
def update_client(request):
    pass


# remove client
def delete_client(request):
    pass


@require_POST
def deactivate(request):
    if request.user.has_perm(OAUTH_LOOKUP_NAME):
        request.user.user_permissions.remove(get_perm(OAUTH_CODENAME))
        request.user.save()
    return redirect('accounts:index')