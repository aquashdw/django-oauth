from django.urls import path

from oauth.views import authorize as authorize_views
from oauth.views import client as client_views

app_name = 'oauth'
urlpatterns = [
    # oauth
    path('activate/', client_views.activate, name='activate'),
    path('deactivate/', client_views.deactivate, name='deactivate'),
    path('', client_views.index, name='index'),
    # clients
    path('create/', client_views.create_client, name='create'),
    path('<int:pk>/', client_views.read_client, name='read'),
    path('<int:pk>/update/', client_views.update_client, name='update'),
    path('<int:pk>/delete/', client_views.delete_client, name='delete'),
    # callbacks
    path('<int:pk>/callbacks/', client_views.add_callback, name='callback_add'),
    path('<int:pk>/callbacks/<int:callback_pk>/', client_views.remove_callback, name='callback_remove'),
    # test_users
    path('<int:pk>/test-users/', client_views.add_test_user, name='testuser_add'),
    path('<int:pk>/test-users/remove/', client_views.remove_test_user, name='testuser_remove'),

    # oauth
    path('authorize/', authorize_views.authorize, name='authorize'),
    path('token/', authorize_views.token, name='token'),
    path('user-info/', authorize_views.get_user_info, name='user_info'),
    path('refresh/', authorize_views.refresh, name='refresh'),
]
