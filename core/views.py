from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from core.models import Team, Department
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
import json
from collections import Counter, defaultdict
from django.db.models import Count
from core.models import Team, Department, TeamMember
from django.http import HttpResponse
import openpyxl
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib import colors
from core.models import Message, MessageStatus
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

@login_required
def visualization(request):
    # Chart 1: Teams per Department
    dept_team_counts = (
        Department.objects
        .annotate(team_count=Count('teams'))
        .order_by('-team_count')
        .values('name', 'team_count')
    )
    chart_teams_per_dept = json.dumps({
        'labels': [d['name'] for d in dept_team_counts],
        'data':   [d['team_count'] for d in dept_team_counts],
    })

    # Chart 2: Department Head vs Project count
    head_to_count = defaultdict(int)
    for dept in Department.objects.all():
        head_label = dept.head if dept.head else '(no head listed)'
        head_to_count[head_label] += dept.teams.count()
    sorted_heads = sorted(head_to_count.items(), key=lambda kv: kv[1], reverse=True)
    chart_head_vs_projects = json.dumps({
        'labels': [k for k, _ in sorted_heads],
        'data':   [v for _, v in sorted_heads],
    })

    # Chart 3: Stacked bar - Department -> Teams
    all_depts = list(Department.objects.prefetch_related('teams').all())
    all_team_names = [t.name for dept in all_depts for t in dept.teams.all()]
    stacked_labels = [d.name for d in all_depts]
    stacked_datasets = []
    for team_name in all_team_names:
        row = []
        for dept in all_depts:
            row.append(1 if dept.teams.filter(name=team_name).exists() else 0)
        if any(row):
            stacked_datasets.append({'label': team_name, 'data': row})
    chart_dept_projects_stack = json.dumps({
        'labels': stacked_labels,
        'datasets': stacked_datasets,
    })

    # Chart 4: Members per team (top 15)
    member_counts = (
        Team.objects
        .annotate(member_count=Count('members'))
        .order_by('-member_count')[:15]
        .values('name', 'member_count')
    )
    chart_members_per_team = json.dumps({
        'labels': [t['name'] for t in member_counts],
        'data':   [t['member_count'] for t in member_counts],
    })

    # Chart 5: Dependency types
    dep_types = Team.objects.values_list('dependency_type', flat=True)
    dep_counter = Counter(d for d in dep_types if d)
    chart_dependency_types = json.dumps({
        'labels': list(dep_counter.keys()),
        'data':   list(dep_counter.values()),
    })

    # Chart 6: Concurrent projects per team (top 10)
    concurrent_teams = []
    for team in Team.objects.all():
        try:
            val = int(team.concurrent_projects)
            concurrent_teams.append((team.name, val))
        except (ValueError, TypeError):
            pass
    concurrent_teams.sort(key=lambda x: x[1], reverse=True)
    concurrent_teams = concurrent_teams[:10]
    chart_concurrent = json.dumps({
        'labels': [t[0] for t in concurrent_teams],
        'data':   [t[1] for t in concurrent_teams],
    })

    # KPIs
    total_teams = Team.objects.count()
    total_members = TeamMember.objects.count()
    kpis = {
        'departments': Department.objects.count(),
        'teams': total_teams,
        'members': total_members,
        'avg_team_size': round(total_members / total_teams, 1) if total_teams else 0.0,
    }

    return render(request, 'visualization.html', {
        'kpis': kpis,
        'chart_teams_per_dept': chart_teams_per_dept,
        'chart_head_vs_projects': chart_head_vs_projects,
        'chart_dept_projects_stack': chart_dept_projects_stack,
        'chart_members_per_team': chart_members_per_team,
        'chart_dependency_types': chart_dependency_types,
        'chart_concurrent': chart_concurrent,
    })

@login_required
def organisation(request):
    departments = Department.objects.prefetch_related('teams').all()
    return render(request, 'organisation.html', {
        'departments': departments,
    })

@login_required
def reports(request):
    total_teams = Team.objects.count()
    total_departments = Department.objects.count()
    teams_without_managers = Team.objects.filter(leader='')
    missing_managers_count = teams_without_managers.count()
    return render(request, 'reports.html', {
        'total_teams': total_teams,
        'total_departments': total_departments,
        'teams_without_managers': teams_without_managers,
        'missing_managers_count': missing_managers_count,
    })

@login_required
def export_pdf(request):
    teams_without_managers = Team.objects.filter(leader='')
    total_teams = Team.objects.count()
    total_departments = Department.objects.count()
    missing_managers_count = teams_without_managers.count()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="sky_report.pdf"'

    p = pdf_canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # Title
    p.setFillColor(colors.HexColor('#00428f'))
    p.setFont("Helvetica-Bold", 20)
    p.drawString(50, height - 60, "Sky Management Report")

    # Summary
    p.setFillColor(colors.black)
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 100, f"Total Departments: {total_departments}")
    p.drawString(50, height - 120, f"Total Teams: {total_teams}")
    p.drawString(50, height - 140, f"Teams Missing Managers: {missing_managers_count}")

    # Table header
    p.setFillColor(colors.HexColor('#d9534f'))
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, height - 180, "Teams Without Managers")

    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, height - 210, "Team Name")
    p.drawString(200, height - 210, "Department")
    p.drawString(350, height - 210, "Dept Head")

    # Table rows
    p.setFont("Helvetica", 10)
    y = height - 230
    for team in teams_without_managers:
        p.drawString(50, y, team.name[:25])
        p.drawString(200, y, team.department.name[:20])
        p.drawString(350, y, team.department.head[:20] if team.department.head else 'N/A')
        y -= 20
        if y < 50:
            p.showPage()
            y = height - 50

    p.save()
    return response

@login_required
def export_excel(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Sky Report'
    ws.append(['Team Name', 'Department', 'Department Head', 'Development Focus'])
    for team in Team.objects.all():
        ws.append([
            team.name,
            team.department.name,
            team.department.head,
            team.development_focus,
        ])
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="sky_report.xlsx"'
    wb.save(response)
    return response

@login_required
def messaging_inbox(request):
    statuses = MessageStatus.objects.filter(
        user=request.user,
        message__is_draft=False
    ).select_related('message__sender').order_by('-message__created_at')
    unread_count = statuses.filter(is_read=False).count()
    return render(request, 'messaging/inbox.html', {
        'statuses': statuses,
        'unread_count': unread_count,
        'active_tab': 'inbox',
    })

@login_required
def messaging_sent(request):
    messages_sent = Message.objects.filter(
        sender=request.user,
        is_draft=False
    ).order_by('-created_at')
    return render(request, 'messaging/sent.html', {
        'messages': messages_sent,
        'active_tab': 'sent',
        'unread_count': 0,
    })

@login_required
def messaging_drafts(request):
    drafts = Message.objects.filter(
        sender=request.user,
        is_draft=True
    ).order_by('-created_at')
    return render(request, 'messaging/drafts.html', {
        'drafts': drafts,
        'active_tab': 'drafts',
        'unread_count': 0,
    })

@login_required
def messaging_compose(request):
    preselected_ids = []
    draft = None
    draft_id = request.GET.get('draft_id')
    to_id = request.GET.get('to')

    if draft_id:
        draft = get_object_or_404(Message, id=draft_id, sender=request.user, is_draft=True)

    if to_id:
        preselected_ids = [int(to_id)]

    if request.method == 'POST':
        subject = request.POST.get('subject')
        body = request.POST.get('body')
        recipient_ids = request.POST.getlist('recipients')
        action = request.POST.get('action')

        recipients = User.objects.filter(id__in=recipient_ids)
        recipient_names = ', '.join([u.get_full_name() or u.username for u in recipients])

        if action == 'send':
            msg = Message.objects.create(
                sender=request.user,
                subject=subject,
                body=body,
                is_draft=False,
                recipient_list=recipient_names,
            )
            msg.recipients.set(recipients)
            for recipient in recipients:
                MessageStatus.objects.create(message=msg, user=recipient, is_read=False)
            if draft:
                draft.delete()
            return redirect('messaging_inbox')

        elif action == 'draft':
            if draft:
                draft.subject = subject
                draft.body = body
                draft.recipient_list = recipient_names
                draft.save()
                draft.recipients.set(recipients)
            else:
                msg = Message.objects.create(
                    sender=request.user,
                    subject=subject,
                    body=body,
                    is_draft=True,
                    recipient_list=recipient_names,
                )
                msg.recipients.set(recipients)
            return redirect('messaging_drafts')

    users = User.objects.exclude(id=request.user.id)
    return render(request, 'messaging/compose.html', {
        'users': users,
        'draft': draft,
        'preselected_ids': preselected_ids,
        'active_tab': 'compose',
        'unread_count': 0,
    })

@login_required
def messaging_detail(request, msg_id):
    msg = get_object_or_404(Message, id=msg_id)
    status = MessageStatus.objects.filter(message=msg, user=request.user).first()
    if status and not status.is_read:
        status.is_read = True
        status.save()
    is_sender = msg.sender == request.user
    return render(request, 'messaging/message_detail.html', {
        'msg': msg,
        'is_sender': is_sender,
        'unread_count': 0,
    })

@login_required
def messaging_delete(request, msg_id):
    msg = get_object_or_404(Message, id=msg_id)
    MessageStatus.objects.filter(message=msg, user=request.user).delete()
    if msg.sender == request.user:
        msg.delete()
    return redirect('messaging_inbox')

@login_required
def messaging_delete_draft(request, draft_id):
    draft = get_object_or_404(Message, id=draft_id, sender=request.user, is_draft=True)
    draft.delete()
    return redirect('messaging_drafts')