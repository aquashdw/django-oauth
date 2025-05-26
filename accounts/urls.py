from django.shortcuts import redirect
from django.urls import path

from accounts import views

app_name = 'accounts'
urlpatterns = [
    path('', lambda _: redirect('accounts:my_profile'), name='index'),
    path('signup/', views.signup, name='signup'),
    path('signup/confirm/', views.signup_confirm, name='signup_confirm'),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
    path('me/', views.my_profile, name='my_profile'),
    path('verify/', views.verify_request, name='verify'),
    # path('profile/<username>/', views.profile, name='profile'),
]
