from django.contrib import admin
from .models import Department, Team
from .models import TeamMember


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'head')
    search_fields = ('name', 'head')

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'leader', 'concurrent_projects')
    search_fields = ('name', 'leader', 'department__name')
    list_filter = ('department',)

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'team', 'email')
    search_fields = ('name', 'role', 'team__name')
    list_filter = ('team',)