from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.template import loader
from .models import Tournament, password_reset_code, Institution, Entry
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
            tourneys = Tournament.objects.filter(endDate__range=[date.today(), "2050-1-1"], approved=True).order_by("startDate")
        else:
            tourneys = Tournament.objects.filter(Q(name__icontains=search_tournament), Q(location__icontains=location_tournament), Q(formats__icontains=format_tournament), Q(startDate__icontains=year_tournament), approved=True).order_by("-startDate")
    else:
        try:
            tourneys = Tournament.objects.filter(endDate__range=[date.today(), "2050-1-1"], approved=True).order_by("startDate") #Remove - to reverse order
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
        if name != '':
            request.user.name = name
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

        #Decline invite
        if "decline_invite_id" in request.POST:
            institution_id_decline = request.POST['decline_invite_id']
            i = Institution.objects.get(id=institution_id_decline)
            u = request.user
            i.pendingMembers.remove(u)
            i.save()
            return redirect('institution')
        
        #Leave institution
        if "leave_inst_id" in request.POST:
            leave_inst_id = request.POST['leave_inst_id']
            i = Institution.objects.get(id=leave_inst_id)
            u = request.user
            i.members.remove(u)
            i.save()
            return redirect('institution')
        
        #Removing a member
        if "delete_member_id" in request.POST:
            delete_member_id = request.POST['delete_member_id']
            delete_member_email = request.POST['delete_member_email']
            i = Institution.objects.get(id=delete_member_id)
            u = TabCenterUser.objects.get(email=delete_member_email)
            i.members.remove(u)
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

################################################################### Tournament Management

@login_required(login_url="/login")
def myTournaments(request):
    tournaments = TabCenterUser.objects.get(id=request.user.id).tournament_set.all()
    context = {"tournaments": tournaments}

    #Editing tournaments
    if request.method == "POST":
        t_id = request.POST["regopenclose_id"]
        t = Tournament.objects.get(id=t_id)
        t.registration = (not t.registration)
        t.save()
        tournaments = TabCenterUser.objects.get(id=request.user.id).tournament_set.all()
        context = {"tournaments": tournaments}

    return render(request, 'TabCenterApp/mytournaments.html', context)

@login_required(login_url="/login")
def createTournament(request):
    if request.method == "POST":
        name = request.POST["TName"]
        city = request.POST["TCity"]
        province = request.POST["TProvince"]
        startDate = request.POST["TstartDate"]
        endDate = request.POST["TendDate"]
        price = float(request.POST["Tprice"])
        regReqs = request.POST["Treg"]
        description = request.POST["Tdescrip"]
        tournament_invite = request.POST["Tinvite"]
        tabbycat_url = request.POST["Ttabby"]
        online = request.POST.get("online")
        if online == "on":
            online = True
        else:
            online = False

        #Formats
        try:
            cndf = (request.POST["cndf"], "CNDF")
        except:
            cndf = ("off", "cndf")

        try:
            bp = (request.POST["bp"], "BP")
        except:
            bp = ("off", "bp")

        try:
            world = (request.POST["world"], "World")
        except:
            world = ("off", "world")

        try:
            crossex = (request.POST["cross-ex"], "Cross-ex")
        except:
            crossex = ("off", "cross-ex")

        try:
            speech = (request.POST["speech"], "Speech")
        except:
            speech = ("off", "speech")

        draft_formats = [cndf, bp, world, crossex, speech]
        formats = [x[1] for x in draft_formats if (x[0] == "on")]

        new_t = Tournament(
            name=name,
            startDate=startDate,
            endDate=endDate,
            location=province,
            organizer=request.user,
            formats=formats,
            price=price,
            online=online,
            city=city,
            tabbyCatLink=tabbycat_url,
            invitationDocLink=tournament_invite,
            registrationRequirements=regReqs,
            description=description
        )
        new_t.save()

        #Send notification email
        send_mail(
                'Tournament Submission',
                f'New tournament awaiting approval called {name}',
                'meadowridge.debate@gmail.com',
                ['meadowridge.debate@gmail.com'],
                fail_silently=False
        )
        return redirect('myTournaments')
        
    return render(request, 'TabCenterApp/createTournament.html')

###################################################################### Tournament Registration

@login_required(login_url="/login")
def registerTournament(request, tournament_id, coach_or_debater, institution_id, formats):
    if request.method == "POST":
        kid_id_1 = request.POST["kid_id_1"]
        member1 = TabCenterUser.objects.get(id=kid_id_1)
        kid_id_2 = request.POST["kid_id_2"]
        member2 = TabCenterUser.objects.get(id=kid_id_2)
        grade_1 = request.POST["grade_1"]
        grade_2 = request.POST["grade_2"]
        inst = Institution.objects.get(id=institution_id)

        new_entry = Entry(member1=member1, member2=member2, member1_grade=grade_1, member2_grade=grade_2, institution=inst, formats=formats)
        new_entry.save()
        i = Tournament.objects.get(id=tournament_id)
        i.entries.add(new_entry)
        i.save()
        return redirect("home")

    kids = Institution.objects.get(id=institution_id).members.all
    if coach_or_debater == 1:
        coach_or_debater = True
    else:
        coach_or_debater = False
    context = {"kids": kids, "coach_or_debater": coach_or_debater, "user_person": request.user}
    return render(request, 'TabCenterApp/register_tournament.html', context)

@login_required(login_url="/login")
def registerSelect(request, tournament_id):
    organizeInstitutions = TabCenterUser.objects.get(id=request.user.id).institution_set.all()
    memberInstitutions = TabCenterUser.objects.get(id=request.user.id).part_of_institutions.all()
    tournament_formats = Tournament.objects.get(id=tournament_id).formats
    if request.method == "POST":
        #Coach
        if "institution_coach" in request.POST:
            institution_id = request.POST["institution_coach"]
            forma = request.POST["institution_format1"]
            coach_or_debater = 1
            
        #Debater
        if "institution_debater" in request.POST:
            institution_id = request.POST["institution_debater"]
            forma = request.POST["institution_format2"]
            coach_or_debater = 0
        
        if Institution.objects.get(id=institution_id).members.count() < 2:
            context = {"organizeInstitutions": organizeInstitutions, "memberInstitutions": memberInstitutions, "tournament_formats": tournament_formats, 'error': True}
            return render(request, 'TabCenterApp/register_select.html', context)
        
        return redirect('registerTournament', tournament_id=tournament_id, coach_or_debater=coach_or_debater, institution_id=institution_id, formats=forma)

    context = {"organizeInstitutions": organizeInstitutions, "memberInstitutions": memberInstitutions, "tournament_formats": tournament_formats, 'error': False}
    return render(request, 'TabCenterApp/register_select.html', context)