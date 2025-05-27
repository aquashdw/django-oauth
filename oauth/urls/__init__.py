from django.urls import include, path

app_name = 'oauth'
urlpatterns = [
    path('', include('oauth.urls.client')),
    path('', include('oauth.urls.authorize')),
]
