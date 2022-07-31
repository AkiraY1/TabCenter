from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.template import loader
from .models import Tournament, password_reset_code, Institution
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from TabCenterApp.models import TabCenterUser
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import send_mail
import uuid
from django.core.paginator import Paginator
from datetime import date
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password

############################################################ Home/Tournament Views

def home(request):
    if request.method == "POST":
        search_tournament = request.POST.get('search')
        if search_tournament == None:
            search_tournament = ""
        format_tournament = request.POST.get('format')
        if format_tournament == None:
            format_tournament = ""
        location_tournament = request.POST.get('location')
        if location_tournament == None:
            location_tournament = ""
        year_tournament = request.POST.get('year')
        if year_tournament == None:
            year_tournament = ""
        attrs = [search_tournament, format_tournament, location_tournament, year_tournament]
        if attrs.count(attrs[0]) == len(attrs):
            tourneys = Tournament.objects.filter(endDate__range=[date.today(), "2050-1-1"]).order_by("startDate")
        else:
            tourneys = Tournament.objects.filter(Q(name__icontains=search_tournament), Q(location__icontains=location_tournament), Q(formats__icontains=format_tournament), Q(startDate__icontains=year_tournament)).order_by("-startDate")
    else:
        try:
            tourneys = Tournament.objects.filter(endDate__range=[date.today(), "2050-1-1"]).order_by("startDate") #Remove - to reverse order
        except:
            raise Http404("Error: No tournaments can be found.")
    #Pagination
    paginator = Paginator(tourneys, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'tourneys': tourneys, 'page_obj': page_obj}
    return render(request, 'TabCenterApp/home.html', context)

def tournament(request, tournament_id):
    try:
        info = Tournament.objects.get(id=tournament_id)
    except:
        raise Http404("Error: No such tournament can be found.")
    output = {'tourney': info}
    return render(request, 'TabCenterApp/tournament.html', output)

################################################################### Auth

def view_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            context = {"error":True}
            return render(request, 'TabCenterApp/login.html', context)
    context = {"error":False}
    return render(request, 'TabCenterApp/login.html', context)

@login_required(login_url="/login")
def view_logout(request):
    logout(request)
    return redirect('/')

def signup(request):
    if request.method == 'POST':
        email = request.POST['email']
        name = request.POST['name']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        
        if (email == "") or (name == "") or (password1 == "") or (password1 == ""):
            context = {"error":"Please fill all fields."}
            return render(request, 'TabCenterApp/signup.html', context)

        try:
            validate_email(email)
        except ValidationError:
            context = {"error":"Please enter a valid email."}
            return render(request, 'TabCenterApp/signup.html', context)

        if password1 != password2:
            context = {"error":"Passwords do not match."}
            return render(request, 'TabCenterApp/signup.html', context)
    
        try:
            validate_password(password2)
        except ValidationError:
            context = {"error":"Please choose a stronger password. Minimum length of 12 characters, cannot be entirely numeric, and no common passwords."}
            return render(request, 'TabCenterApp/signup.html', context)

        try: 
            user = TabCenterUser.objects.get(email=email)
            context = {"error":"Account already exists for this email."}
            return render(request, 'TabCenterApp/signup.html', context)
        except TabCenterUser.DoesNotExist:
            user = TabCenterUser.objects.create_user(email, name, password2)
            login(request, user)
            return redirect('/')

    context = {"error":False}
    return render(request, 'TabCenterApp/signup.html', context)

@login_required(login_url="/login")
def account(request):
    if request.method == 'POST':
        name = request.POST['name']
        paradigm = request.POST['paradigm']
        if name != '':
            request.user.name = name
        if paradigm != request.user.paradigm:
            request.user.paradigm = paradigm
        request.user.save()
        return render(request, 'TabCenterApp/account.html')
    return render(request, 'TabCenterApp/account.html')

def password_reset(request):
    if request.method == 'POST':
        email = request.POST['email']
        if (email != '') and not (not TabCenterUser.objects.filter(email=email)):
            hash = uuid.uuid4().hex
            h = password_reset_code(email=email, code=hash)
            h.save()
            send_mail(
                'TabCenter Password Change',
                f'Your code is: {hash}. Enter it on the webpage.',
                'meadowridge.debate@gmail.com',
                [email],
                fail_silently=False
            )
            return redirect('password_reset_submit')
    return render(request, 'TabCenterApp/password-reset.html')

def password_reset_submit(request):
    if request.method == 'POST':
        email = request.POST['email']
        code = request.POST['code']
        password = request.POST['password']
        r = password_reset_code.objects.filter(email=email, code=code)
        if not r:
            return render(request, 'TabCenterApp/password-reset-submit.html')
        else:
            u = TabCenterUser.objects.get(email=email)
            u.set_password(password)
            u.save()
            return redirect('view_login')
        
    return render(request, 'TabCenterApp/password-reset-submit.html')

################################################################### Institutions

@login_required(login_url="/login")
def institution(request):
    organizeInstitutions = TabCenterUser.objects.get(id=request.user.id).institution_set.all()
    memberInstitutions = TabCenterUser.objects.get(id=request.user.id).part_of_institutions.all()
    pendingInstitutions = TabCenterUser.objects.get(id=request.user.id).pending_part_of_institutions.all()
    context = {"institutions": organizeInstitutions, "memberInstitutions": memberInstitutions, "pendingInstitutions": pendingInstitutions}

    if request.method == "POST":

        #Name Change
        if "inst_name" in request.POST:
            inst_id = request.POST['institution_id']
            inst_name = request.POST['inst_name']
            if inst_name != "":
                i = Institution.objects.get(id=inst_id)
                i.name = inst_name
                try:
                    i.save()
                    organizeInstitutions = TabCenterUser.objects.get(id=request.user.id).institution_set.all()
                    context = {"institutions": organizeInstitutions, "memberInstitutions": memberInstitutions, "pendingInstitutions": pendingInstitutions}
                except:
                    return render(request, 'TabCenterApp/institution.html', context)
            return redirect('institution')

        #Delete Institution
        if "institution_id_delete" in request.POST:
            inst_id_delete = request.POST['institution_id_delete']
            i = Institution.objects.get(id=inst_id_delete)
            i.delete()
            organizeInstitutions = TabCenterUser.objects.get(id=request.user.id).institution_set.all()
            context = {"institutions": organizeInstitutions, "memberInstitutions": memberInstitutions, "pendingInstitutions": pendingInstitutions}
        
        #Add new member
        if "email_user_add" in request.POST:
            email_user_add = request.POST['email_user_add']
            institution_id_add_member = request.POST['institution_id_add_member']
            try:
                u = TabCenterUser.objects.get(email=email_user_add)
            except:
                return render(request, 'TabCenterApp/institution.html', context)
            i = Institution.objects.get(id=institution_id_add_member)
            i.pendingMembers.add(u)
            i.save()
            return redirect('institution')
        
        #Accept invite
        if "accept_invite_id" in request.POST:
            institution_id_invite = request.POST['accept_invite_id']
            i = Institution.objects.get(id=institution_id_invite)
            u = request.user
            i.pendingMembers.remove(u)
            i.members.add(u)
            i.save()
            return redirect('institution')

    return render(request, 'TabCenterApp/institution.html', context)

@login_required(login_url="/login")
def createInstitution(request):
    if request.method == 'POST':
        institutionName = request.POST['institutionName']
        if institutionName == "":
            context = {'errors':"Please enter an institution name."}
            return render(request, 'TabCenterApp/createInstitution.html', context)

        currentUser = request.user
        try:
            i = Institution(name=institutionName, organizer=currentUser)
            i.save()
            return redirect('institution')
        except:
            context = {'errors':"Institution name already taken."}
            return render(request, 'TabCenterApp/createInstitution.html', context)

    context = {'errors':None}
    return render(request, 'TabCenterApp/createInstitution.html', context)