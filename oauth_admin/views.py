from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch
from django.shortcuts import render, get_object_or_404

from oauth.models import OAuthClient


def superuser_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return _wrapped_view


@superuser_required
def index(request):
    clients = OAuthClient.objects.filter(status=OAuthClient.REVIEWING)
    context = {
        'clients': clients,
    }
    return render(request, 'oauth_admin/index.html', context)


@superuser_required
def review(request, client_pk):
    client = get_object_or_404(
        OAuthClient.objects.prefetch_related(
            'test_users',
            Prefetch('callback_urls'),
            Prefetch('review_set'),
        ),
        pk=client_pk
    )
    context = {
        'client': client,
        'callback_urls': client.callback_urls.all(),
        'test_users': client.test_users.all(),
        'reviews': client.review_set.all(),
    }
    return render(request, 'oauth_admin/review.html', context)
