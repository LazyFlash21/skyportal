from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('teams/', views.teams, name='teams'),
    path('teams/<int:team_id>/', views.team_detail, name='team_detail'),
    path('profile/', views.profile, name='profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('schedule/', views.schedule, name='schedule'),
    path('visualization/', views.visualization, name='visualization'),
    path('organisation/', views.organisation, name='organisation'),
    path('reports/', views.reports, name='reports'),
    path('export-pdf/', views.export_pdf, name='export_pdf'),
    path('export-excel/', views.export_excel, name='export_excel'),
    path('messages/', views.messaging_inbox, name='messaging_inbox'),
    path('messages/sent/', views.messaging_sent, name='messaging_sent'),
    path('messages/drafts/', views.messaging_drafts, name='messaging_drafts'),
    path('messages/compose/', views.messaging_compose, name='messaging_compose'),
    path('messages/<int:msg_id>/', views.messaging_detail, name='messaging_detail'),
    path('messages/delete/<int:msg_id>/', views.messaging_delete, name='messaging_delete'),
    path('messages/delete-draft/<int:draft_id>/', views.messaging_delete_draft, name='messaging_delete_draft'),
]

