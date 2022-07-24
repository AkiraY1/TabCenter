from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('tournament/<int:tournament_id>/', views.tournament, name='tournament')
]