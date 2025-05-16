from functools import wraps

from django.forms import BaseForm
from django.shortcuts import redirect

def extract_form_errors(form: BaseForm):
    errors = []
    error_data = form.errors.as_data()
    for error_param in error_data:
        param_errors = error_data[error_param]
        for error in param_errors:
            errors.append(error.code)

    return errors


def anonymous(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('accounts:index')
        return view_func(request, *args, **kwargs)

    return _wrapped_view
