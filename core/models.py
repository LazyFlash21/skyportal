from django.db import models
from django.contrib.auth.models import User

class Department(models.Model):
    name = models.CharField(max_length=100)
    head = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Team(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='teams')
    name = models.CharField(max_length=100)
    leader = models.CharField(max_length=100)
    jira_project = models.CharField(max_length=100, blank=True, null=True)
    github_repo = models.CharField(max_length=200, blank=True, null=True)
    jira_board = models.CharField(max_length=200, blank=True, null=True)
    development_focus = models.TextField(blank=True, null=True)
    key_skills = models.TextField(blank=True, null=True)
    downstream_dependencies = models.CharField(max_length=200, blank=True, null=True)
    dependency_type = models.CharField(max_length=100, blank=True, null=True)
    slack_channels = models.CharField(max_length=200, blank=True, null=True)
    standup_time = models.CharField(max_length=100, blank=True, null=True)
    agile_practices = models.CharField(max_length=200, blank=True, null=True)
    team_wiki = models.CharField(max_length=200, blank=True, null=True)
    concurrent_projects = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name

class TeamMember(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members')
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    skills = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} – {self.team.name}"
    
class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipients = models.ManyToManyField(User, related_name='received_messages')
    subject = models.CharField(max_length=200)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_draft = models.BooleanField(default=False)
    recipient_list = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return f"{self.subject} – {self.sender.username}"

class MessageStatus(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='statuses')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.message.subject} – {self.user.username}"