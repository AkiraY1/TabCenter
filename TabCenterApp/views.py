from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import Tournament

def home(request):
    tourneys = Tournament.objects.all()
    output = {'tourneys': tourneys}
    return render(request, 'TabCenterApp/home.html', output)