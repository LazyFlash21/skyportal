 Sky Engineering Portal
A Django-based web application that replaces Sky's Excel-based engineering team registry with a centralised, database-driven portal. Built as part of the University of Westminster 5COSC021W Software Development Group Project.

📋 Project Overview
Sky's Global Apps Engineering team maintains a registry of all engineering teams in an Excel spreadsheet. This application replaces that spreadsheet with a fully functional web portal where users can:

Search and browse all 46 engineering teams across 6 departments
View full team details including mission, contacts, Slack channels, GitHub repositories, skills and dependencies
Send internal messages between users
Schedule and manage meetings
Generate PDF and Excel management reports
Visualise organisational data through interactive charts

🛠️ Tech Stack

Backend: Django 6.0.4, Python 3.12
Database: SQLite
Frontend: HTML5, CSS3, JavaScript
Charts: Chart.js 4.4.1
PDF Export: ReportLab
Excel Export: OpenPyXL
Version Control: Git / GitHub


🚀 Getting Started
Prerequisites

Python 3.12+
pip

Installation
1. Clone the repository
bashgit clone https://github.com/YOURUSERNAME/skyportal.git
cd skyportal
2. Install dependencies
bashpip install django
pip install openpyxl
pip install reportlab
3. Set up the database
bashpython manage.py migrate
4. Import Sky team data
bashpython import_data.py
python add_members.py
5. Create an admin account
bashpython manage.py createsuperuser
6. Run the server
bashpython manage.py runserver
7. Open your browser and visit
http://127.0.0.1:8000


📄 Pages
URLPageDescription/DashboardStats, recent teams, quick actions/teams/TeamsBrowse and search all 46 teams/teams/<id>/Team DetailFull team info, members, dependencies/organisation/OrganisationDepartments and team structure/messages/MessagesInternal messaging system/schedule/ScheduleMeeting calendar and scheduling/reports/ReportsPDF and Excel management reports/visualization/Data Visualisation6 interactive Chart.js charts/login/LoginUser authentication/register/RegisterNew user registration/profile/ProfileUser profile management/admin/Admin PanelDjango admin interface

🗄️ Database Models
ModelDescriptionDepartmentSky engineering departments (6 departments)TeamEngineering teams (46 teams)TeamMemberTeam engineers (230 members)MessageInternal messages between usersMessageStatusRead/unread status per user

🔐 Default Credentials
Admin Panel (/admin/):

Create your own superuser with python manage.py createsuperuser

Test User:

Register a new account at /register/


🔒 Security

All views protected with @login_required
CSRF tokens on all forms
Django's built-in password hashing (PBKDF2)
SQL injection prevention via Django ORM
Admin restricted to superuser accounts


📊 Data
The application is pre-loaded with real Sky Engineering team data including:

6 departments: xTV_Web, Mobile, Native TVs, Arch, Reliability_Tool, Programme
46 teams with full details including Slack channels, GitHub repos, skills and dependencies
230 engineers across all teams
