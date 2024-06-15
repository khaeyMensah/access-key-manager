from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from .tokens import account_activation_token

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout
from access_keys.models import AccessKey, KeyLog, School
from django.contrib import messages
from users.models import BillingInformation, User
from users.forms import ProfileUpdateForm, RegistrationForm, LoginForm, ProfileForm, UpdateBillingInformationForm
from users.contexts import common_context_data


# Create your views here.
def home(request):
    context = common_context_data(request)
    return render(request, 'users/home.html', context)


@login_required
@user_passes_test(lambda u: u.is_school_personnel)
def school_dashboard_view(request):
    if not request.user.is_school_personnel:
        return redirect('access_denied')
    
    try:
        school = request.user.school
        access_keys = school.access_keys.order_by('-procurement_date')
    except School.DoesNotExist:
        messages.error(request, 'No school associated with your account.')
        return redirect('complete_profile')
    except AttributeError:
        messages.error(request, 'Error retrieving access keys. Complete your profile.')
        return redirect('complete_profile')
    
    context = common_context_data(request)
    context.update ({
        'school': school,
        'access_keys': access_keys,
    })
    return render(request, 'users/school_dashboard.html', context)

        
        
@login_required
@user_passes_test(lambda u: u.is_admin)
def admin_dashboard_view(request):
    if not request.user.is_admin:
        return redirect('access_denied')

    if not request.user.first_name or not request.user.last_name or not request.user.staff_id:
        messages.error(request, 'Please complete your profile to access the admin dashboard.')
        return redirect('complete_profile')

    access_keys = AccessKey.objects.order_by('-procurement_date')
    key_logs = KeyLog.objects.order_by('-timestamp')
    
    context = common_context_data(request)
    context.update ({
        'access_keys': access_keys,
        'key_logs': key_logs,    
    })
    return render(request, 'users/admin_dashboard.html', context)


def registration_options_view(request):
    return render(request, 'accounts/register_options.html')


def register_view(request, user_type):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            if user_type == 'school_personnel':
                user.is_school_personnel = True
            elif user_type == 'admin':
                user.is_admin = True
            user.save()
            send_verification_email(request, user)
            messages.success(request, 'Registration successful. Please confirm your email.')
            return redirect('registration_pending')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def send_verification_email(request, user):
    current_site = get_current_site(request)
    mail_subject = 'Activate your account.'
    message = render_to_string('authentication/acc_active_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
    })
    to_email = user.email
    send_mail(mail_subject, message, 'ekmpizarro@gmail.com', [to_email])


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your account has been activated successfully!')
        return redirect('activation_success')
    else:
        messages.error(request, 'Activation link is invalid!')
        return render(request, 'authentication/activation_invalid.html')


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, 'Login successful.')
            return redirect('home')
        else:
            messages.error(request, 'Login failed. Please check your credentials.')
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

    context = common_context_data(request)
    context.update ({
        'user': user,
        'active_key': active_key,
    })
    return render(request, 'users/profile.html', context)


@login_required
def billing_information_view(request):
    user = request.user
    try:
        billing_info = BillingInformation.objects.get(user=user)
    except BillingInformation.DoesNotExist:
        return redirect('confirm_billing_info') 
    
    context = common_context_data(request)
    context.update ({
        'billing_info': billing_info,
    })
    return render(request, 'users/billing_information.html', context)


@login_required
def profile_complete_view(request):
    user = request.user
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            if not user.is_admin and not user.school:
                user.school = form.cleaned_data.get('school')
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('home')

    else:
        form = ProfileForm(instance=user)
        if user.is_admin:
            form.fields.pop('school', None)
        else:
            if user.school:
                form.fields.pop('school', None)
            form.fields.pop('staff_id', None)

    context = {
        'form': form
    }
    return render(request, 'users/complete_profile.html', context)


@login_required
def update_billing_information_view(request):
    billing_information, created = BillingInformation.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UpdateBillingInformationForm(request.POST, instance=billing_information)
        if form.is_valid():
            form.save()
            messages.success(request, 'Billing information updated successfully.')
            return redirect('profile')
    else:
        form = UpdateBillingInformationForm(instance=billing_information)

    context = common_context_data(request)
    context.update ({
        'form': form,
    })
    return render(request, 'users/update_billing_info.html', context)


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

    context = common_context_data(request)
    context.update ({
        'profile_form': profile_form,
    })
    return render(request, 'users/update_profile.html', context)
