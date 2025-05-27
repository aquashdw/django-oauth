from django.urls import path

from oauth.views import authorize as views

urlpatterns = [
    # oauth
    path('authorize/', views.authorize, name='authorize'),
    path('revoke/<int:client_pk>/', views.revoke, name='revoke'),
    path('token/', views.token, name='token'),
    path('user-info/', views.get_user_info, name='user_info'),
    path('refresh/', views.refresh, name='refresh'),
]
