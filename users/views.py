from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from .tokens import account_activation_token

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout
from users.helpers import is_school_personnel, is_admin
from access_keys.models import AccessKey, KeyLog, School
from django.contrib import messages
from users.models import BillingInformation, User
from users.forms import ProfileUpdateForm, RegistrationForm, LoginForm, ProfileForm, UpdateBillingInformationForm
from users.contexts import common_context_data


# Create your views here.
def home(request):
    """
    This function renders the home page for authenticated users.

    Args:
        request: The HTTP request object.

    Returns:
        A rendered HTML response containing the home page.
    """
    context = common_context_data(request)
    return render(request, 'users/home.html', context)


@login_required
@user_passes_test(is_school_personnel)
def school_dashboard_view(request):
    """
    This function renders the school dashboard page for authenticated school personnel.

    Args:
        request: The HTTP request object.

    Returns:
        A rendered HTML response containing the school dashboard page.

    Raises:
        Redirect: If the user is not a school personnel.
    """
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
    context.update({
        'school': school,
        'access_keys': access_keys,
    })
    return render(request, 'users/school_dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def admin_dashboard_view(request):
    """
    This function renders the admin dashboard page for authenticated admins users.

    Args:
        request: The HTTP request object.

    Returns:
        A rendered HTML response containing the admin dashboard page.

    Raises:
        Redirect: If the user is not an admin.
    """
    if not request.user.is_admin:
        return redirect('access_denied')

    if not request.user.first_name or not request.user.last_name or not request.user.staff_id:
        messages.error(request, 'Please complete your profile to access the admin dashboard.')
        return redirect('complete_profile')

    access_keys = AccessKey.objects.order_by('-procurement_date')
    key_logs = KeyLog.objects.order_by('-timestamp')

    context = common_context_data(request)
    context.update({
        'access_keys': access_keys,
        'key_logs': key_logs,
    })
    return render(request, 'users/admin_dashboard.html', context)


def registration_options_view(request):
    """
    This function renders the registration options page.

    Args:
        request: The HTTP request object.

    Returns:
        A rendered HTML response containing the registration options page.
    """
    return render(request, 'accounts/register_options.html')


def register_view(request, user_type):
    """
    This function handles the registration process for different user types.

    Args:
        request: The HTTP request object.
        user_type: The type of user being registered (e.g., 'school_personnel', 'admin').

    Returns:
        A rendered HTML response containing the registration form.

    Raises:
        Redirect: If the request method is not POST.
    """
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
    """
    This function sends a verification email to the newly registered user.

    Args:
        request: The HTTP request object.
        user: The newly registered user.

    Returns:
        A rendered HTML response containing the verification email.
    """
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
    """
    This function activates the user's account after clicking the verification link.

    Args:
        request: The HTTP request object.
        uidb64: The base64-encoded user ID.
        token: The activation token.

    Returns:
         HttpResponse: Redirect to login on success, otherwise activation failure page.
    """
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



# def account_activation_sent(request):
#     """
#     Renders the account activation sent page.
    
#     Args:
#         request (HttpRequest): The request object.
    
#     Returns:
#         HttpResponse: The rendered account activation sent page.
#     """
#     return render(request, 'users/account_activation_sent.html')

# def account_activation_invalid(request):
#     """
#     Renders the account activation invalid page.
    
#     Args:
#         request (HttpRequest): The request object.
    
#     Returns:
#         HttpResponse: The rendered account activation invalid page.
#     """
#     return render(request, 'users/account_activation_invalid.html')




def login_view(request):
    """
    This function handles the user login  by rendering the login form and authenticating users.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: The rendered login page or redirect to home on success.
    """
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
    """
    This function logs out the user and redirects to the home page.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: Redirect to home page.
    """
    logout(request)
    messages.success(request, 'Logout successful.')
    return redirect('home')


@login_required
def profile_view(request):
    """
    This function renders the user profile page.

    Args:
        request: The HTTP request object.

    Returns:
        A rendered HTML response containing the user profile page.
    """
    user = request.user
    school = user.school

    active_key = None
    if school:
        active_key = school.access_keys.filter(status='active').first()

    context = common_context_data(request)
    context.update({
        'user': user,
        'active_key': active_key,
    })
    return render(request, 'users/profile.html', context)


@login_required
def billing_information_view(request):
    """
    This function renders the user's billing information page.

    Args:
        request: The HTTP request object.

    Returns:
        A rendered HTML response containing the user's billing information page.
    """
    user = request.user
    try:
        billing_info = BillingInformation.objects.get(user=user)
    except BillingInformation.DoesNotExist:
        return redirect('update_billing_info')

    context = common_context_data(request)
    context.update({
        'billing_info': billing_info,
    })
    return render(request, 'users/billing_information.html', context)


@login_required
def profile_complete_view(request):
    """
    This function handles the completion of the user's profile.

    Args:
        request: The HTTP request object.

    Returns:
        A rendered HTML response containing the profile completion form.

    Raises:
        Redirect: If the user's profile is already complete.
    """
    user = request.user

    if user.is_profile_complete():
        messages.info(request, 'Your profile is already complete.')
        return redirect('profile')

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            if user.is_school_personnel and not user.school:
                user.school = form.cleaned_data.get('school')
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileForm(instance=user)
        if user.is_admin:
            form.fields.pop('school')
        else:
            if user.school:
                form.fields['school'].disabled = True
            form.fields.pop('staff_id')

    context = {
        'form': form,
    }
    return render(request, 'users/complete_profile.html', context)


@login_required
def update_billing_information_view(request):
    """
    This function handles the update of the user's billing information.

    Args:
        request: The HTTP request object.

    Returns:
        A rendered HTML response containing the billing information update form.
    """
    billing_information, created = BillingInformation.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UpdateBillingInformationForm(request.POST, instance=billing_information)
        if form.is_valid():
            form.save()
            messages.success(request, 'Billing information updated successfully.')
            return redirect('billing_information')
    else:
        form = UpdateBillingInformationForm(instance=billing_information)

    context = common_context_data(request)
    context.update({
        'form': form,
    })
    return render(request, 'users/update_billing_info.html', context)


@login_required
def update_profile_view(request):
    """
    This function handles the update of the user's profile.

    Args:
        request: The HTTP request object.

    Returns:
        A rendered HTML response containing the profile update form.
    """
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
    context.update({
        'profile_form': profile_form,
    })
    return render(request, 'users/update_profile.html', context)
