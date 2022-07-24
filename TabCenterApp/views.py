from django.shortcuts import render
from django.http import HttpResponse
from .models import Tournament

def home(request):
    tourneys = Tournament.objects.all()
    output = ', '.join(x.name for x in tourneys)
    return HttpResponse(output)