from django.urls import path

from oauth_admin import views

app_name = 'oauth_admin'
urlpatterns = [
    path('', views.index, name='index'),
    path('client/<int:client_pk>/review/', views.review, name='review'),
]
