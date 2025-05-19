from django.urls import path

from oauth import views

app_name = 'oauth'
urlpatterns = [
    path('activate/', views.activate, name='activate'),
    path('', views.index, name='index'),
    path('create/', views.create_client, name='create'),
    path('<int:pk>/', views.read_client, name='read'),
    path('<int:pk>/update/', views.update_client, name='update'),
    path('<int:pk>/delete/', views.delete_client, name='delete'),
    path('deactivate/', views.deactivate, name='deactivate'),
]
