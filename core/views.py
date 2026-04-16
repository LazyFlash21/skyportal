from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from core.models import Team, Department
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User

def forgot_password(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        new_password = request.POST.get('new_password1')
        confirm_password = request.POST.get('new_password2')
        
        try:
            user = User.objects.get(username=username)
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                return redirect('login')
            else:
                return render(request, 'forgot_password.html', {'error': 'Passwords do not match'})
        except User.DoesNotExist:
            return render(request, 'forgot_password.html', {'error': 'Username not found'})
    
    return render(request, 'forgot_password.html')


@login_required
def profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        return redirect('profile')
    return render(request, 'profile.html')

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('profile')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    total_teams = Team.objects.count()
    total_depts = Department.objects.count()
    teams = Team.objects.all()[:5]
    departments = Department.objects.all()
    return render(request, 'dashboard.html', {
        'total_teams': total_teams,
        'total_depts': total_depts,
        'teams': teams,
        'departments': departments,
    })

@login_required
def teams(request):
    query = request.GET.get('q', '')
    dept_filter = request.GET.get('dept', '')
    teams = Team.objects.all()
    
    if query:
        teams = teams.filter(
            Q(name__icontains=query) |
            Q(department__name__icontains=query) |
            Q(leader__icontains=query)
        )
    
    if dept_filter:
        teams = teams.filter(department__id=dept_filter)

    departments = Department.objects.all()
    return render(request, 'teams.html', {
        'teams': teams,
        'departments': departments,
        'query': query,
        'dept_filter': dept_filter,
    })


@login_required
def schedule(request):
    return render(request, 'schedule.html')

@login_required
def team_detail(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    members = team.members.all()
    return render(request, 'team_detail.html', {
        'team': team,
        'members': members,
    })