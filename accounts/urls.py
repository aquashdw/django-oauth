from django.urls import path

from accounts import views

app_name = 'accounts'
urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('signup/confirm/', views.signup_confirm, name='signup_confirm'),
    # path('signin/', views.signin, name='signin'),
    # path('profile/<username>/', views.profile, name='profile'),
]
