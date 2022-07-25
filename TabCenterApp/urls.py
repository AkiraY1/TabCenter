from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib import admin

urlpatterns = [
    path('', views.home, name='home'),
    path('tournament/<int:tournament_id>/', views.tournament, name='tournament'),
    path('login', views.view_login, name='login'),
    path('logout', views.view_logout, name='logout'),
    path('signup', views.signup, name='signup'),
    path('account', views.account, name='account'),
    path('change-password', auth_views.PasswordChangeView.as_view(template_name='TabCenterApp/change-password.html', success_url='/'), name='change_password')
]