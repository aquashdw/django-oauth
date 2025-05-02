from urllib.parse import urlencode
from django.shortcuts import redirect, render
from django.urls import reverse

from accounts.forms import CustomUserCreationForm


def index(request):
    return render(request, 'accounts/index.html')


def signup(request):
    # return redirect(f'{base_url}?{params}')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.is_active = False
            # instance.save()
            return redirect(f'{reverse("accounts:index")}?{urlencode({"success": "true"})}')
        
        base_url = reverse('accounts:signup')
        errors = []
        error_data = form.errors.as_data()
        for error_param in error_data:
            param_errors = error_data[error_param]
            for error in param_errors:
                errors.append(error.code)         

        errors = ','.join(errors)
        email = form.data.get('email')
        params = {
            'errors': errors,
            'email': email,
        }
        params = urlencode(params)
        return redirect(f'{base_url}?{params}')
    
    form = CustomUserCreationForm()
    context = {
        'form': form,
        'errors': request.GET.get('errors', '').split(','),
        'email': request.GET.get('email', None),
    }
    print(context['errors'])
    
    return render(request, 'accounts/signup.html', context)
