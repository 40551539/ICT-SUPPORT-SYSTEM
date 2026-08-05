from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class User(AbstractUser):
    """Custom User with role-based access."""

    class Role(models.TextChoices):
        STUDENT = 'student', 'Student'
        STAFF = 'staff', 'Staff'
        TECHNICIAN = 'technician', 'Technician'
        ADMIN = 'admin', 'Admin'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
    )
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)

    # 🔹 New field for admission number (students only)
    admission_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        unique=True,
        help_text="Format: 12/XXXXX (for students only)"
    )

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

    @property
    def is_technician(self):
        return self.role == self.Role.TECHNICIAN

    @property
    def is_admin_user(self):
        return self.role == self.Role.ADMIN


class EmailVerification(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='email_verification'
    )
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Verification for {self.user.username}"
