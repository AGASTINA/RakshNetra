from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import User

@require_http_methods(["GET", "POST"])
def signup(request):
    """User signup view"""
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        role = request.POST.get('role', User.ROLE_VIEWER)

        # Validation
        if not all([username, email, password1, password2]):
            messages.error(request, "All fields are required")
            return render(request, 'accounts/signup.html', {
                'roles': User.ROLE_CHOICES
            })

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return render(request, 'accounts/signup.html', {
                'roles': User.ROLE_CHOICES
            })

        if len(password1) < 12:
            messages.error(request, "Password must be at least 12 characters")
            return render(request, 'accounts/signup.html', {
                'roles': User.ROLE_CHOICES
            })

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return render(request, 'accounts/signup.html', {
                'roles': User.ROLE_CHOICES
            })

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return render(request, 'accounts/signup.html', {
                'roles': User.ROLE_CHOICES
            })

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            role=role
        )
        messages.success(request, "Account created successfully. Please log in.")
        return redirect('login')

    return render(request, 'accounts/signup.html', {
        'roles': User.ROLE_CHOICES
    })

@require_http_methods(["GET", "POST"])
def login_view(request):
    """User login view"""
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'accounts/login.html')

@login_required(login_url='login')
def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect('login')

@login_required(login_url='login')
def profile(request):
    """User profile view"""
    return render(request, 'accounts/profile.html', {
        'user': request.user
    })
