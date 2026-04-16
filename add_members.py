import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyportal.settings')
django.setup()

from core.models import Team, TeamMember

# Clear existing members
TeamMember.objects.all().delete()

# Fake member templates
roles = ['Senior Engineer', 'Backend Developer', 'Frontend Developer', 'DevOps Engineer', 'QA Engineer']
first_names = ['James', 'Sarah', 'Mohammed', 'Emma', 'Lucas', 'Aisha', 'Daniel', 'Priya', 'Oliver', 'Fatima']
last_names = ['Smith', 'Johnson', 'Ali', 'Wilson', 'Brown', 'Khan', 'Jones', 'Patel', 'Taylor', 'Ahmed']

teams = Team.objects.all()

for i, team in enumerate(teams):
    for j in range(5):
        first = first_names[(i + j) % len(first_names)]
        last = last_names[(i + j * 2) % len(last_names)]
        role = roles[j % len(roles)]
        email = f"{first.lower()}.{last.lower()}@sky.uk"
        TeamMember.objects.create(
            team=team,
            name=f"{first} {last}",
            role=role,
            email=email,
            skills=team.key_skills[:50] if team.key_skills else 'Python, Django'
        )

print(f"Done! Added {TeamMember.objects.count()} members across {teams.count()} teams")