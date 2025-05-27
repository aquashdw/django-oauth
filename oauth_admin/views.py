from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch
from django.shortcuts import render, get_object_or_404

from django_oauth.utils import redirect_with_nq
from oauth.models import OAuthClient
from oauth_admin.forms import ReviewForm


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

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.client = client
            instance.save()
            client.status = instance.decision
            client.save()
            return redirect_with_nq('oauth_admin:index', {'review': 'success'})
        return redirect_with_nq('oauth_admin:review', {'review': 'reason'}, client_pk)

    context = {
        'client': client,
        'callback_urls': client.callback_urls.all(),
        'test_users': client.test_users.all(),
        'reviews': client.review_set.all(),
    }
    return render(request, 'oauth_admin/review.html', context)
