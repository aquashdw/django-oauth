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
            instance.save()
            return redirect(f'{reverse("accounts:index")}?{urlencode({"success": "true"})}')
        
        base_url = reverse('accounts:signup')
        errors = {
            'errors': ','.join(form.error_messages.keys())
        }
        params = urlencode(errors)
        return redirect(f'{base_url}?{params}')
    
    form = CustomUserCreationForm()
    context = {
        'form': form,
    }
    return render(request, 'accounts/signup.html', context)
