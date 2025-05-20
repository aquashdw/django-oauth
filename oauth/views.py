from uuid import uuid4

from django.contrib.auth.decorators import permission_required, login_required
from django.db.models import Prefetch
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_safe

from django_oauth.utils import get_perm, redirect_with_nq, extract_form_errors
from oauth.forms import OAuthClientForm
from oauth.models import OAuthClient

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
@require_safe
@permission_required(OAUTH_LOOKUP_NAME, login_url='oauth:activate')
def index(request):
    clients = OAuthClient.objects.filter(owner=request.user)
    context = {
        'clients': clients,
    }

    return render(request, 'oauth/index.html', context)


@permission_required(OAUTH_LOOKUP_NAME, login_url='oauth:activate')
def create_client(request):
    if request.method == 'POST':
        form = OAuthClientForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.owner = request.user
            instance.client_id = str(uuid4()).replace('-', '')
            instance.client_secret = str(uuid4()).replace('-', '')
            instance.save()
            return redirect_with_nq('oauth:index', {'created': 'true'})

        params = {
            'errors': ','.join(extract_form_errors(form)),
        }
        return redirect_with_nq('oauth:create', params)

    context = {
        'errors': request.GET.get('errors', '').split(','),
    }

    return render(request, 'oauth/create.html', context)


# read one client
def read_client(request, pk):
    client = get_object_or_404(OAuthClient.objects.prefetch_related(
            'test_users',
            Prefetch('callback_urls'),
        ),
        pk=pk
    )

    if (client.status == OAuthClient.DELETED or
            client.owner != request.user):
        raise Http404

    context = {
        'client': client,
    }
    return render(request, 'oauth/details.html', context)


# update client
def update_client(request):
    pass


# remove client
def delete_client(request):
    pass


def deactivate(request):
    if not request.user.has_perm(OAUTH_LOOKUP_NAME):
        return redirect('accounts:index')

    if request.method == 'GET':
        return render(request, 'oauth/deactivate.html')

    if request.method == 'POST':
        request.user.user_permissions.remove(get_perm(OAUTH_CODENAME))
        request.user.save()

    return redirect('accounts:index')