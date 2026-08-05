from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserUpdateForm
from .models import EmailVerification


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.save()
            messages.success(request, 'Account created successfully. Please log in.')
            return redirect('users:login')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})


def verify_email(request):
    user_id = request.session.get('verify_user_id')
    if not user_id:
        return redirect('users:register')

    from .models import User
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return redirect('users:register')

    if request.method == 'POST':
        entered = request.POST.get('code', '').strip()
        try:
            verification = user.email_verification
        except EmailVerification.DoesNotExist:
            messages.error(request, 'Verification record not found. Please register again.')
            return redirect('users:register')

        from django.utils import timezone
        import datetime
        age = timezone.now() - verification.created_at
        if age > datetime.timedelta(minutes=10):
            messages.error(request, 'Code expired. Please register again.')
            user.delete()
            return redirect('users:register')

        if entered == verification.code:
            user.is_active = True
            user.save()
            verification.delete()
            del request.session['verify_user_id']
            login(request, user, backend='users.backends.EmailBackend')
            messages.success(request, f'Email verified! Welcome, {user.first_name or user.username}.')
            return redirect('reports:dashboard')
        else:
            messages.error(request, 'Incorrect code. Please try again.')

    return render(request, 'users/verify_email.html', {'email': user.email})


@login_required
def profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('users:profile')
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'users/profile.html', {'form': form})
