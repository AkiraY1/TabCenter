from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib import admin

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('tournament/<int:tournament_id>/', views.tournament, name='tournament'),
    path('login/', views.view_login, name='login'),
    path('logout/', views.view_logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('account/', views.account, name='account'),
    path('change-password/', auth_views.PasswordChangeView.as_view(template_name='TabCenterApp/change-password.html', success_url='/account'), name='change_password'),
    path('password-reset/', views.password_reset, name='password_reset'),
    path('password-reset-submit/', views.password_reset_submit, name='password_reset_submit'),
    path('institution/', views.institution, name='institution'),
    path('create-institution/', views.createInstitution, name='createInstitution'),
    path('my-tournaments/', views.myTournaments, name='myTournaments'),
    path('create-tournament/', views.createTournament, name='createTournament'),
    path('register-select/<int:tournament_id>/', views.registerSelect, name='registerSelect'),
    path('register-tournament/<int:tournament_id>/<int:coach_or_debater>/<int:institution_id>/<str:formats>/<int:number_debaters>/', views.registerTournament, name='registerTournament'),
]