import re

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=100, required=True,
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Sharon'})
    )
    last_name = forms.CharField(
        max_length=100, required=True,
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Ondieki'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'you@example.com'})
    )
    role = forms.ChoiceField(choices=User.Role.choices, initial=User.Role.STUDENT)
    department = forms.CharField(
        max_length=100, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Finance, ICT, Registry'})
    )
    phone = forms.CharField(
        max_length=20, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'e.g. +254 700 000 000'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'role', 'department', 'phone', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'placeholder': 'Min. 8 characters'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Repeat your password'})
        for field in self.fields.values():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select auth-input'})
            else:
                field.widget.attrs.update({'class': 'form-control auth-input'})

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip().lower()

        if not email:
            return email

        if not email.endswith('@cuea.edu'):
            raise forms.ValidationError('Only CUEA email addresses are allowed. Use an email ending with @cuea.edu.')

        local_part = email.split('@', 1)[0]
        role = (self.cleaned_data.get('role') or self.data.get('role') or '').lower()

        if role == User.Role.STUDENT:
            if not local_part.isdigit():
                raise forms.ValidationError('Student accounts must use a CUEA student email like 1049528@cuea.edu.')
        elif not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*', local_part):
            raise forms.ValidationError('Staff, technician, and admin accounts must use a valid CUEA email like Sharonbossy@cuea.edu.')

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        # Auto-generate a unique username from email prefix
        base = self.cleaned_data['email'].split('@')[0].lower()
        username = base
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base}{counter}"
            counter += 1
        user.username = username
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'department']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
