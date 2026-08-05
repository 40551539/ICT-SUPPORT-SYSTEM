# CUEA ICT Help Desk Support System

A Django-based help desk platform for the Catholic University of Eastern Africa (CUEA) ICT Department to manage technical support requests.

---

## Project Overview

This system allows CUEA students, staff, and administrators to:
- submit support tickets
- track ticket progress
- assign and resolve issues
- review ticket history and feedback
- manage role-based access for staff and students

---

## Project Structure

```
ICT HELP DESK SUPPORT SYSTEM/
├── config/               # Django project configuration
│   ├── settings.py       # Project settings (database, apps, middleware)
│   ├── urls.py           # Main URL routing
│   ├── asgi.py           # ASGI configuration (for async)
│   └── wsgi.py           # WSGI configuration (for production)
│
├── users/                # User authentication & management app
│   ├── models.py         # User model definitions
│   ├── views.py          # Login, register, profile views
│   ├── forms.py          # User forms
│   ├── urls.py           # User app routes
│   └── admin.py          # Django admin configuration
│
├── tickets/              # Ticket management app
│   ├── models.py         # Ticket model (status, priority, etc.)
│   ├── views.py          # Ticket detail and list views
│   ├── forms.py          # Ticket creation/update forms
│   ├── urls.py           # Ticket routes
│   └── admin.py          # Ticket admin interface
│
├── reports/              # Issue reporting app
│   ├── models.py         # Report model definitions
│   ├── views.py          # Report creation and listing
│   ├── forms.py          # Report forms
│   ├── urls.py           # Report routes
│   └── admin.py          # Report admin interface
│
├── templates/            # HTML templates
│   ├── base.html         # Base template (layout, navbar, footer)
│   ├── landing.html      # Public landing page
│   ├── tickets/          # Ticket templates
│   ├── users/            # User templates (login, register)
│   └── reports/          # Report templates
│
├── static/               # Static files (CSS, JS, images)
│   └── img/              # Images (logo, icons)
│
├── .venv/                # Python virtual environment (local)
│
├── manage.py             # Django management script
├── requirements.txt      # Project dependencies
└── README.md             # This file
```

---

## Tech Stack

- Django
- SQLite for local development
- Bootstrap 5 for the UI
- Python 3.x
- Django templates and standard project structure

---

## Installation & Setup

### 1. Clone or extract the project
```bash
cd "ICT HELP DESK SUPPORT SYSTEM"
```

### 2. Create a virtual environment
```bash
python -m venv .venv
```

### 3. Activate the environment

Windows PowerShell:
```powershell
.venv\Scripts\Activate.ps1
```

Windows CMD:
```cmd
.venv\Scripts\activate.bat
```

macOS/Linux:
```bash
source .venv/bin/activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Apply database migrations
```bash
python manage.py migrate
```

### 6. Create a superuser
```bash
python manage.py createsuperuser
```

### 7. Collect static files (if needed)
```bash
python manage.py collectstatic --noinput
```

---

## Running the Project

Start the development server:
```bash
python manage.py runserver
```

Open:
```text
http://127.0.0.1:8000
```

Admin route:
```text
http://127.0.0.1:8000/admin
```

---

## Key Features

### 1. User management
- registration and authentication
- profile management
- student, staff, and admin roles

### 2. Ticket management
- create and view tickets
- track status: open, in progress, resolved, closed
- assign tickets to staff
- add comments and resolutions

### 3. Reporting and dashboard views
- student and staff dashboard views
- reporting pages and summaries
- ticket analytics and workflow handling

---

## Database Models

### Users App
- `User` — Extended Django user model with roles and profiles

### Tickets App
- `Ticket` — Main ticket model with status, priority, and assignment fields
- `TicketComment` — Comments/updates on tickets

### Reports App
- `Report` — Issue report with category, description, and status

---

## Configuration

For local development you can use the default SQLite setup.

If you want to switch to PostgreSQL later, update the database settings in `config/settings.py`.

---

## Common Commands

| Command | Purpose |
|---------|---------|
| `python manage.py runserver` | Start development server |
| `python manage.py migrate` | Apply database migrations |
| `python manage.py makemigrations [app_name]` | Create new migrations after model changes |
| `python manage.py createsuperuser` | Create admin account |
| `python manage.py collectstatic` | Collect static files for production |
| `python manage.py shell` | Open interactive Python shell with Django context |
| `python manage.py test` | Run automated tests |

---

## URL Routes

| Route | Purpose |
|-------|---------|
| `/` | landing page |
| `/tickets/` | view user tickets |
| `/tickets/[id]/` | ticket detail page |
| `/users/login/` | login |
| `/users/register/` | registration |
| `/users/profile/` | user profile |
| `/admin/` | admin dashboard |

---

## Support

For questions or issues, contact the CUEA ICT department.

---

## License

This project is developed for the Catholic University of Eastern Africa (CUEA).
