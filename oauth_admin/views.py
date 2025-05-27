from django.core.exceptions import PermissionDenied
from django.shortcuts import render


def superuser_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return _wrapped_view


@superuser_required
def index(request):
    return render(request, 'oauth_admin/index.html')


@superuser_required
def review(request, pk):
    return render(request, 'oauth_admin/review.html')
