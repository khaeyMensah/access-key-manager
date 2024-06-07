from django import forms
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout
from access_keys.models import AccessKey, KeyLog, School
from django.contrib import messages
from users.models import BillingInformation
from users.forms import BillingInformationForm, ProfileUpdateForm, RegistrationForm, LoginForm, UserCompleteForm


# Create your views here.
def home(request):
    return render(request, 'users/home.html')


@login_required
@user_passes_test(lambda u: u.is_school_personnel)
def school_dashboard_view(request):
    if not request.user.is_school_personnel:
        return redirect('access_denied')
    
    try:
        school = request.user.school
    except School.DoesNotExist:
        messages.error(request, 'No school associated with your account.')
        return redirect('complete_profile')

    access_keys = school.access_keys.order_by('-procurement_date')
    
    context = {
        'school': school,
        'access_keys': access_keys,
    }
    return render(request, 'users/school_dashboard.html', context)

        
        
@login_required
@user_passes_test(lambda u: u.is_admin)
def admin_dashboard_view(request):
    if not request.user.is_admin:
        return redirect('access_denied')

    # access_keys = school.access_keys.all()
    access_keys = AccessKey.objects.order_by('-procurement_date')
    key_logs = KeyLog.objects.order_by('-timestamp')
    
    context = {
        'access_keys': access_keys,
        'key_logs': key_logs,    
    }
    return render(request, 'users/admin_dashboard.html', context)


def registration_options_view(request):
    return render(request, 'accounts/register_options.html')


def register_view(request, user_type):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if user_type == 'school_personnel':
                user.is_school_personnel = True
                messages.success(request, 'School personnel registration successful.')
            elif user_type == 'admin':
                user.is_admin = True
                messages.success(request, 'Admin registration successful.')
            user.save()
            auth_login(request, user)
            return redirect('complete_profile')
    else:
        form = RegistrationForm()
        
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, 'Login successful.')
            if user.is_admin:
                return redirect('admin_dashboard')
            else:
                return redirect('school_dashboard')
            
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Logout successful.')
    return redirect('home')


@login_required
def profile_view(request):
    user = request.user
    school = user.school

    active_key = None
    if school:
        active_key = school.access_keys.filter(status='active').first()

    context = {
        'user': user,
        'active_key': active_key,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def billing_information_view(request):
    user = request.user
    try:
        billing_info = BillingInformation.objects.get(user=user)
    except BillingInformation.DoesNotExist:
        return redirect('confirm_billing_info') 
    context = {
        'billing_info': billing_info,
    }
    return render(request, 'accounts/billing_information.html', context)


@login_required
def profile_complete_view(request):
    user = request.user
    
    if request.method == 'POST':
        form = UserCompleteForm(request.POST, instance=user)
        if form.is_valid():
            if not user.is_admin and not user.school:
                user.school = form.cleaned_data.get('school')
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = UserCompleteForm(instance=user)
        if user.is_admin or user.school:
            form.fields.pop('school', None)

    context = {
        'form': form
    }
    return render(request, 'accounts/complete_profile.html', context)


@login_required
def confirm_billing_information_view(request):
    try:
        billing_info = request.user.billing_information
    except BillingInformation.DoesNotExist:
        billing_info = None

    if request.method == 'POST':
        form = BillingInformationForm(request.POST, instance=billing_info)
        if form.is_valid():
            billing_info = form.save(commit=False)
            billing_info.user = request.user
            billing_info.save()
            messages.success(request, 'Billing information updated successfully.')
            return redirect('school_dashboard')
    else:
        form = BillingInformationForm(instance=billing_info)
        form.fields['email'].initial = request.user.email
        

    context = {
        'form': form,
    }
    return render(request, 'accounts/confirm_billing_info.html', context)


@login_required
def update_billing_information_view(request):
    return confirm_billing_information_view(request)


@login_required
def update_profile_view(request):
    if request.method == 'POST':
        profile_form = ProfileUpdateForm(request.POST, instance=request.user)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        profile_form = ProfileUpdateForm(instance=request.user)

    context = {
        'profile_form': profile_form,
    }
    return render(request, 'accounts/update_profile.html', context)


