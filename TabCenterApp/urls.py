from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('tournament/<int:tournament_id>/', views.tournament, name='tournament'),
    path('login', views.view_login, name='login'),
    path('logout', views.view_logout, name='logout'),
    path('signup', views.signup, name='signup'),
    path('account', views.account, name='account'),
]