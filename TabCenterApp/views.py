from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.template import loader
from .models import Tournament

def home(request):
    try:
        tourneys = Tournament.objects.order_by("startDate")
    except:
        raise Http404("Error: No tournaments can be found.") #Goes to standard 404 page
    output = {'tourneys': tourneys}
    return render(request, 'TabCenterApp/home.html', output)

def tournament(request, tournament_id):
    try:
        info = Tournament.objects.get(id=tournament_id)
    except:
        raise Http404("Error: No such tournament can be found.")
    output = {'tourney': info}
    return render(request, 'TabCenterApp/tournament.html', output)