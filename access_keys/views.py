from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.http import HttpResponse
from django.views.decorators.http import require_GET
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
import requests

from access_keys.models import AccessKey, KeyLog
from users.contexts import common_context_data
from users.forms import BillingInformationForm
from users.helpers import is_admin, is_school_personnel
from users.models import School, User
from .utils import generate_access_key

# import random



# Create your views here.
@login_required
@user_passes_test(is_school_personnel)
@permission_required('users.can_purchase_access_key', raise_exception=True)
def purchase_access_key_view(request):
    """
    This view handles the purchase of an access key for a school.

    Args:
        request: The HTTP request object.

    Returns:
        If the purchase is successful, redirects to the school dashboard.
        If the purchase fails, displays an error message.

    Raises:
        If the user already has an active access key, an error message is displayed.

    """
    school = get_object_or_404(School, users=request.user)
    active_keys = school.access_keys.filter(status='active')

    if active_keys.exists():
        messages.error(request, 'You already have an active access key.')
        return redirect('school_dashboard')

    billing_info = getattr(request.user, 'billing_information', None)

    if request.method == 'POST':
        form = BillingInformationForm(request.POST, instance=billing_info)
        print("Form data:", request.POST)  # Debugging
        if form.is_valid():
            print("Form is valid")  # Debugging
            if form.cleaned_data.get('confirm_purchase'):
                billing_info = form.save(commit=False)
                billing_info.user = request.user
                billing_info.save()
                return redirect('access_keys:initialize_payment')

            else:
                messages.error(request, 'You must confirm the purchase to proceed.')
        else:
            print("Form errors:", form.errors)  # Debugging
            messages.error(request, 'Please provide valid billing information.')
    else:
        form = BillingInformationForm(instance=billing_info)

    context = common_context_data(request)
    context.update({
        'form': form,
        'school': school,
        'access_key_price': settings.ACCESS_KEY_PRICE,
        'PAYSTACK_SETTINGS': settings.PAYSTACK_SETTINGS,
    })
    return render(request, 'access_keys/purchase_access_key.html', context)

@login_required
def initialize_payment(request):
    if request.method == 'POST':
        billing_info = request.user.billing_information
        if not billing_info:
            messages.error(request, 'Billing information is missing.')
            return redirect('access_keys:purchase_access_key')

        url = f"{settings.PAYSTACK_SETTINGS.get('BASE_URL', 'https://api.paystack.co')}/transaction/initialize"
        headers = {
            'Authorization': f'Bearer {settings.PAYSTACK_SETTINGS["SECRET_KEY"]}',
            'Content-Type': 'application/json',
        }
        data = {
            'email': billing_info.email,
            'amount': int(settings.ACCESS_KEY_PRICE * 100),  # Convert to pesewas
            'currency': 'GHS',
            'callback_url': settings.PAYSTACK_SETTINGS['CALLBACK_URL'],
        }
        print("Initializing payment with data:", data)  # Debugging
        response = requests.post(url, headers=headers, json=data)
        print("Paystack response:", response.status_code, response.json())  # Debugging

        if response.status_code == 200:
            authorization_url = response.json()['data']['authorization_url']
            return redirect(authorization_url)
        else:
            messages.error(request, 'Unable to initialize payment.')
            return redirect('access_keys:purchase_access_key')
    return redirect('access_keys:purchase_access_key')

@require_GET
def paystack_callback(request):
    reference = request.GET.get('reference')
    if not reference:
        return HttpResponse('No reference supplied')

    url = f"{settings.PAYSTACK_SETTINGS.get('BASE_URL', 'https://api.paystack.co')}/transaction/verify/{reference}"
    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SETTINGS["SECRET_KEY"]}',
    }
    response = requests.get(url, headers=headers)
    result = response.json()

    if result['status']:
        # Payment was successful
        amount = result['data']['amount'] / 100  # Convert from pesewas to your Cedis
        email = result['data']['customer']['email']

        user = get_object_or_404(User, email=email)
        school = get_object_or_404(School, users=user)

        # Create access key
        procurement_date = timezone.now().date()
        expiry_date = procurement_date + timezone.timedelta(days=1)
        access_key = AccessKey.objects.create(
            school=school,
            key=generate_access_key(),
            status='active',
            assigned_to=user,
            procurement_date=procurement_date,
            expiry_date=expiry_date,
            price=amount,
        )

        KeyLog.objects.create(
            access_key=access_key,
            action=f'Access key {access_key.key} purchased for school {school.name}',
            user=user
        )

        messages.success(request, 'Payment successful. Access key purchased.')
    else:
        messages.error(request, 'Payment failed.')

    return redirect('school_dashboard')



@login_required
@user_passes_test(is_admin)
@permission_required('users.can_revoke_access_key', raise_exception=True)
def revoke_access_key_view(request, key_id):
    """
    This view handles the revocation of an access key by an admin.

    Args:
        request: The HTTP request object.
        key_id: The ID of the access key to be revoked.

    Returns:
        If the revocation is successful, redirects to the admin dashboard.

    Raises:
        If the access key does not exist, an error message is displayed.

    """
    access_key = get_object_or_404(AccessKey, id=key_id)
    if request.method == 'POST':
        access_key.status = 'revoked'
        access_key.revoked_by = request.user
        access_key.revoked_on = timezone.now()
        access_key.save()

        KeyLog.objects.create(
            access_key=access_key,
            action=f'Access key {access_key.key} revoked for school {access_key.school.name}',
            user=request.user,
        )

        messages.success(request, 'Access key revoked successfully.')
        return redirect('admin_dashboard')

    context = common_context_data(request)
    context.update({
        'access_key': access_key,
    })
    return render(request, 'access_keys/revoke_access_key.html', context)

