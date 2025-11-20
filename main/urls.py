from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('upload/', views.upload_route, name='upload_route'),
    path('route/<int:route_id>/delete/', views.delete_route, name='delete_route'),
    path('route/<int:route_id>/edit/', views.edit_route, name='edit_route'),
    path('', views.home, name='home'),
    path('api/routes/', views.route_api, name='route_api'),
]
