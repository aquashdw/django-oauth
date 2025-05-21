from django.urls import path

from oauth import views

app_name = 'oauth'
urlpatterns = [
    # oauth
    path('activate/', views.activate, name='activate'),
    path('deactivate/', views.deactivate, name='deactivate'),
    path('', views.index, name='index'),
    # clients
    path('create/', views.create_client, name='create'),
    path('<int:pk>/', views.read_client, name='read'),
    path('<int:pk>/update/', views.update_client, name='update'),
    path('<int:pk>/delete/', views.delete_client, name='delete'),
    # callbacks
    path('<int:pk>/callbacks/', views.add_callback, name='callback_add'),
    path('<int:pk>/callbacks/<int:callback_pk>/', views.remove_callback, name='callback_remove'),
    # test_users
    path('<int:pk>/test-users/', views.add_test_user, name='testuser_add'),
    path('<int:pk>/test-users/remove/', views.remove_test_user, name='testuser_remove'),

    # oauth
    path('authorize/', views.authorize, name='authorize'),
    path('token/', views.token, name='token'),
]
