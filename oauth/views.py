from uuid import uuid4

from django.contrib.auth.decorators import permission_required, login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_safe, require_POST, require_http_methods

from django_oauth.utils import get_perm, redirect_with_nq, extract_form_errors
from oauth.forms import OAuthClientForm, CallbackUrlForm
from oauth.models import OAuthClient, CallbackUrl

OAUTH_CODENAME = 'oauth_active'
OAUTH_LOOKUP_NAME = 'oauth.oauth_active'


@login_required
def activate(request):
    if request.user.has_perm(OAUTH_LOOKUP_NAME):
        return redirect('oauth:index')

    if request.method == 'POST':
        request.user.user_permissions.add(get_perm(OAUTH_CODENAME))
        request.user.save()
        return redirect('oauth:index')

    return render(request, 'oauth/activate.html')


@require_safe
@permission_required(OAUTH_LOOKUP_NAME, login_url='oauth:activate')
def index(request):
    clients = (OAuthClient.objects
               .filter(owner=request.user)
               .exclude(status=OAuthClient.DELETED))
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


@require_safe
@permission_required(OAUTH_LOOKUP_NAME, login_url='oauth:activate')
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
        'callback_urls': client.callback_urls.all(),
        'test_users': client.test_users.all(),
    }
    return render(request, 'oauth/details.html', context)


@require_POST
@permission_required(OAUTH_LOOKUP_NAME, login_url='oauth:activate')
def update_client(request, pk):
    client = get_object_or_404(OAuthClient, pk=pk)
    if request.user != client.owner:
        raise PermissionDenied
    form = OAuthClientForm(request.POST, instance=client)
    if form.is_valid():
        form.save()
        return redirect_with_nq('oauth:read', {'rename': 'true'}, pk)

    params = {
        'errors': 'clientname',
    }
    return redirect_with_nq('oauth:read', params, pk)


@require_http_methods(['GET', 'POST'])
@permission_required(OAUTH_LOOKUP_NAME, login_url='oauth:activate')
def delete_client(request, pk):
    client = get_object_or_404(OAuthClient, pk=pk)
    if request.user != client.owner:
        raise PermissionDenied

    if request.method == 'GET':
        return render(request, 'oauth/delete.html', { 'client': client })

    client.status = OAuthClient.DELETED
    client.save()
    return redirect_with_nq('oauth:index', {'delete': 'true'})


@login_required
@permission_required(OAUTH_LOOKUP_NAME, login_url='accounts:index')
def deactivate(request):
    if request.method == 'GET':
        return render(request, 'oauth/deactivate.html')

    if request.method == 'POST':
        request.user.user_permissions.remove(get_perm(OAUTH_CODENAME))
        request.user.save()

    return redirect('accounts:index')


@require_POST
@permission_required(OAUTH_LOOKUP_NAME, login_url='oauth:activate')
def add_callback(request, pk):
    client = get_object_or_404(OAuthClient, pk=pk)
    if request.user != client.owner:
        raise PermissionDenied

    if not client.callback_urls.count() < 4:
        return redirect_with_nq('oauth:read', {'callback': 'exceed_limit'}, pk)

    form = CallbackUrlForm(request.POST)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.client = client
        instance.save()
        return redirect_with_nq('oauth:read', {'callback': 'add'}, pk)

    return redirect_with_nq('oauth:read', {'callback': 'error'}, pk)

@require_POST
@permission_required(OAUTH_LOOKUP_NAME, login_url='oauth:activate')
def remove_callback(request, pk, callback_pk):
    client = get_object_or_404(OAuthClient, pk=pk)
    if request.user != client.owner:
        raise PermissionDenied
    callback = get_object_or_404(CallbackUrl, pk=callback_pk)
    callback.delete()
    return redirect_with_nq('oauth:read', {'callback': 'delete'}, pk)
