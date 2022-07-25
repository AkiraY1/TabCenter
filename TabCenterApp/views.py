from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.template import loader
from .models import Tournament
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from TabCenterApp.models import TabCenterUser

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

def view_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            return render(request, 'TabCenterApp/login.html')
    return render(request, 'TabCenterApp/login.html')

def view_logout(request):
    logout(request)
    return redirect('/')

def signup(request):
    if request.method == 'POST':
        email = request.POST['email']
        name = request.POST['name']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        
        if password1 == password2:
            try: 
                user = TabCenterUser.objects.get(email=email)
                return render(request, 'TabCenterApp/signup.html')
            except TabCenterUser.DoesNotExist:
                user = TabCenterUser.objects.create_user(email, name, password2)
                return redirect('/logout')
        else:
            return render(request, 'TabCenterApp/signup.html')
    return render(request, 'TabCenterApp/signup.html')

@login_required(login_url="/login")
def account(request):
    return render(request, 'TabCenterApp/account.html')