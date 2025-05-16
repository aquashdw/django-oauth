from functools import wraps

from django.shortcuts import redirect


def anonymous(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('accounts:index')
        return view_func(request, *args, **kwargs)

    return _wrapped_view
