from django.urls import path
from . import views

urlpatterns = [
    path('accounts/login/', views.auth_view, name='login'),
    path('password_reset/', views.password_reset, name='password_reset'),
    path('logout/', views.user_logout, name='logout'),
    path('send_code/', views.send_verification_code, name='send_code'),
    path('', views.home, name='home'),
    path('category/<int:category_id>/', views.service_list, name='service_list'),
    path('service/<int:service_id>/order/', views.create_order, name='create_order'),
    path('terms/', views.terms_view, name='terms'),
    path('privacy/', views.privacy_view, name='privacy'),
]
