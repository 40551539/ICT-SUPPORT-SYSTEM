# CUEA ICT Help Desk Support System

A Django-based help desk support system designed for the Catholic University of Eastern Africa (CUEA) ICT Department to manage and track technical support tickets.

---

## 📋 Project Overview

The ICT Help Desk Support System is a web application that enables CUEA students, staff, and administrators to:
- **Report technical issues** — Submit support requests with detailed descriptions
- **Track tickets** — Monitor the status of reported issues in real-time
- **Receive updates** — Get notifications on ticket progress and resolution
- **Access knowledge base** — Self-serve solutions for common IT problems
- **Manage requests** — Admin dashboard for IT staff to assign and resolve tickets

---

## 🏗️ Project Structure

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

## 🛠️ Tech Stack

- **Framework**: Django 4.x
- **Database**: SQLite (development) / PostgreSQL (production-ready)
- **Template Engine**: Django Templates with Bootstrap 5
- **Frontend**: HTML5, CSS3, JavaScript (Bootstrap 5 framework)
- **Static Files**: WhiteNoise middleware for efficient serving
- **Server**: Django development server (python manage.py runserver)
- **Python Version**: 3.8+

---

## 📦 Installation & Setup

### 1. **Clone or Extract the Project**
```bash
cd "ICT HELP DESK SUPPORT SYSTEM"
```

### 2. **Create Virtual Environment**
```bash
python -m venv .venv
```

### 3. **Activate Virtual Environment**

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
.venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

### 4. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 5. **Apply Database Migrations**
```bash
python manage.py migrate
```

### 6. **Create a Superuser (Admin Account)**
```bash
python manage.py createsuperuser
```
Follow the prompts to enter username, email, and password.

### 7. **Collect Static Files** (if needed)
```bash
python manage.py collectstatic --noinput
```

---

## 🚀 Running the Project

### Start Development Server
```bash
python manage.py runserver
```

The application will be available at:
```
http://127.0.0.1:8000
```

### Access Admin Dashboard
Navigate to:
```
http://127.0.0.1:8000/admin
```
Log in with your superuser credentials created in Step 6.

---

## 🔑 Key Features

### 1. **User Management** (`users/` app)
- User registration and authentication
- Profile management
- Role-based access (student, staff, admin)
- Login/logout functionality

### 2. **Ticket Management** (`tickets/` app)
- Create and view support tickets
- Track ticket status (open, in progress, resolved, closed)
- Set priority levels (low, medium, high, urgent)
- Assign tickets to support staff
- Add comments and updates to tickets

### 3. **Issue Reporting** (`reports/` app)
- Report technical issues from the landing page
- Quick-start interface for end-users
- Category selection (network, hardware, software, etc.)
- Attachment support for screenshots/logs

### 4. **Landing Page** (`templates/landing.html`)
- Public-facing home page
- Quick links to report issues, login, and register
- Knowledge base section with self-service articles
- FAQ section with common support questions
- System status indicator

### 5. **Admin Dashboard**
- Manage users, tickets, and reports
- View analytics and ticket statistics
- Configure system settings

---

## 📝 Database Models

### Users App
- `User` — Extended Django user model with roles and profiles

### Tickets App
- `Ticket` — Main ticket model with status, priority, and assignment fields
- `TicketComment` — Comments/updates on tickets

### Reports App
- `Report` — Issue report with category, description, and status

---

## 🔧 Configuration

### Environment Variables (Optional but Recommended for Production)
Create a `.env` file in the project root:

```env
DEBUG=False
SECRET_KEY=your-secure-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@localhost:5432/helpdesk_db
```

### Database Configuration
Edit `config/settings.py` to switch from SQLite to PostgreSQL:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'helpdesk_db',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

---

## 📚 Common Commands

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

## 🌐 URL Routes

| Route | App | Purpose |
|-------|-----|---------|
| `/` | reports | Landing page |
| `/reports/report-issue/` | reports | Create a new report |
| `/tickets/` | tickets | View user's tickets |
| `/tickets/[id]/` | tickets | View ticket details |
| `/users/login/` | users | User login |
| `/users/register/` | users | User registration |
| `/users/profile/` | users | User profile |
| `/admin/` | django.admin | Admin dashboard |

---

## 🔐 Security Notes

⚠️ **Before deploying to production:**

1. Change `SECRET_KEY` in `config/settings.py` to a secure, random value
2. Set `DEBUG = False`
3. Configure `ALLOWED_HOSTS` with your actual domain names
4. Use environment variables for sensitive data
5. Set up HTTPS/SSL certificate
6. Use PostgreSQL instead of SQLite
7. Configure a proper email backend for notifications
8. Enable CSRF protection and other security middleware settings

---

## 📞 Support & Contact

For questions or issues with this help desk system, contact:
- **ICT Department** — CUEA
- **Email**: ict@cuea.edu

---

## 📄 License

This project is developed for Catholic University of Eastern Africa (CUEA).

---

## 🎯 Future Enhancements

- [ ] Email notifications for ticket updates
- [ ] SMS alerts for urgent tickets
- [ ] Advanced ticket filtering and search
- [ ] Knowledge base article management
- [ ] Ticket assignment automation
- [ ] Performance metrics and reporting dashboard
- [ ] Integration with external tools (Slack, Teams)
- [ ] Multi-language support (English, Kiswahili)

---

**Last Updated**: March 4, 2026  
**Version**: 1.0
