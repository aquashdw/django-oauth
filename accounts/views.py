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
            form.save()
            return redirect('accounts:index', success='true')
        
        base_url = reverse('accounts:signup')
        params = urlencode({'errors': form.error_messages})
        return redirect(f'{base_url}?{params}')
    
    form = CustomUserCreationForm()
    context = {
        'form': form,
    }
    return render(request, 'accounts/signup.html', context)
