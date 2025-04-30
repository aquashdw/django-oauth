from django.urls import path

from accounts import views

app_name = 'accounts'
urlpatterns = [
    path('', views.index, name='index'),
    # path('signin/', views.signin, name='signin'),
    # path('signup/', views.signup, name='signup'),
    # path('profile/<username>/', views.profile, name='profile'),
]
