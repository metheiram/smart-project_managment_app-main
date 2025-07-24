from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from .forms import UserUpdateForm, ProfileForm, PreferenceForm

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash  # For password change
from .forms import (
    CustomUserCreationForm,
    CustomAuthenticationForm,
    ProfileForm,
    UserUpdateForm,
    PreferenceForm
)

from .models import Profile


User = get_user_model()



def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Check if profile is complete
            if (
                hasattr(user, 'profile') and 
                user.profile.bio.strip() and 
                user.profile.skills.strip() and 
                user.profile.department.strip()
                                                ):
                    return redirect('dashboard')
            else:
                 return redirect('users:profile_setup')
        else:
            if User.objects.filter(username=username).exists():
                messages.error(request, "Invalid password.")
            else:
                messages.error(request, "Account does not exist. Please sign up.")
                return redirect('signup')

    return render(request, 'users/login.html', {'form': CustomAuthenticationForm()})


def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully. Redirecting to dashboard.")
            return redirect('users:profile_setup')  # Corrected here
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'users/register.html', {'form': form})


@login_required
def profile_setup_view(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile setup completed successfully!")
            return redirect('dashboard')  # Corrected here
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)

    return render(request, 'users/profile_setup.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })



def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect('users:login')




@login_required
def settings_view(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        password_form = PasswordChangeForm(request.user, request.POST)
        preference_form = PreferenceForm(request.POST, instance=request.user)

        if 'update_profile' in request.POST:
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, "✅ Profile updated successfully.")
                return redirect('users:settings')

        elif 'change_password' in request.POST:
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "🔒 Password changed successfully.")
                return redirect('users:settings')
            else:
                messages.error(request, "❌ Please correct the error below.")

        elif 'save_preferences' in request.POST:
            if preference_form.is_valid():
                preference_form.save()
                messages.success(request, "⚙️ Preferences saved successfully.")
                return redirect('users:settings')

    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
        password_form = PasswordChangeForm(request.user)
        preference_form = PreferenceForm(instance=request.user)

    return render(request, 'users/settings.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'password_form': password_form,
        'preference_form': preference_form,
    })



@login_required
def profile_view(request):
    user = request.user
    profile = user.profile

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('users:profile')
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = ProfileForm(instance=profile)

    return render(request, 'users/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })