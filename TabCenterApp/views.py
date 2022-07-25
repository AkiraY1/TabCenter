from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.template import loader
from .models import Tournament
from django.db.models import Q

def home(request):
    search_tournament = request.GET.get('search')
    if search_tournament:
        tourneys = Tournament.objects.filter(Q(name__icontains=search_tournament))
    else:
        try:
            tourneys = Tournament.objects.order_by("-startDate") #Remove - to reverse order
        except:
            raise Http404("Error: No tournaments can be found.")
    output = {'tourneys': tourneys}
    return render(request, 'TabCenterApp/home.html', output)

def tournament(request, tournament_id):
    try:
        info = Tournament.objects.get(id=tournament_id)
    except:
        raise Http404("Error: No such tournament can be found.")
    output = {'tourney': info}
    return render(request, 'TabCenterApp/tournament.html', output)