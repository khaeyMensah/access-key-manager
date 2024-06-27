from datetime import timedelta
import logging
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from django.views.decorators.http import require_GET
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.utils import timezone
import requests

from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from access_keys.models import AccessKey, KeyLog
from users.contexts import common_context_data
from users.forms import BillingInformationForm
from users.helpers import is_admin, is_school_personnel, user_passes_test_with_403
from users.models import School, User
from .utils import generate_access_key


logger = logging.getLogger(__name__)

@login_required
@user_passes_test_with_403(is_school_personnel)
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
    # Get the school related to the logged-in user
    school = get_object_or_404(School, users=request.user)
    active_keys = school.access_keys.filter(status='active')

    # Check if there's already an active access key
    if active_keys.exists():
        messages.error(request, 'You already have an active access key.')
        return redirect('school_dashboard')

    billing_info = getattr(request.user, 'billing_information', None)

    if request.method == 'POST':
        form = BillingInformationForm(request.POST, instance=billing_info, user=request.user)
        if form.is_valid():
            if form.cleaned_data.get('confirm_purchase'):
                # Save billing information and redirect to payment initialization
                billing_info = form.save(commit=False)
                billing_info.user = request.user
                billing_info.save()
                logger.info("Billing information saved. Redirecting to initialize payment.")
                return redirect('access_keys:initialize_payment')
            else:
                messages.error(request, 'You must confirm the purchase to proceed.')
                logger.warning("Purchase not confirmed by user.")
        else:
            messages.error(request, 'Please provide valid billing information.')
            logger.warning("Invalid billing information provided.")
    else:
        form = BillingInformationForm(instance=billing_info, user=request.user)

    context = common_context_data(request)
    context.update({
        'form': form,
        'school': school,
        'access_key_price': settings.ACCESS_KEY_PRICE,
        'PAYSTACK_SETTINGS': settings.PAYSTACK_SETTINGS,
    })
    logger.info("Rendering purchase access key page.")
    return render(request, 'access_keys/purchase_access_key.html', context)


@login_required
def initialize_payment(request):
    """
    This view handles the initialization of a payment for purchasing an access key.

    Args:
        request: The HTTP request object.

    Returns:
        If the payment initialization is successful, redirects to the authorization URL provided by the payment gateway.
        If the payment initialization fails, displays an error message.

    Raises:
        If the user's billing information is missing, an error message is displayed.

    """
    if request.method == 'POST':
        user = request.user
        billing_info = user.billing_information
        if not billing_info:
            messages.error(request, 'Billing information is missing.')
            logger.error("Billing information is missing for user.")
            return redirect('access_keys:purchase_access_key')

        base_url = settings.PAYSTACK_SETTINGS.get('BASE_URL', 'https://api.paystack.co')
        callback_url = settings.PAYSTACK_SETTINGS['CALLBACK_URL']

        url = f"{base_url}/transaction/initialize"
        headers = {
            'Authorization': f'Bearer {settings.PAYSTACK_SETTINGS["SECRET_KEY"]}',
            'Content-Type': 'application/json',
        }
        data = {
            'email': user.email,
            'amount': int(settings.ACCESS_KEY_PRICE * 100),  # Convert from cedis to pesewas
            'currency': 'GHS',
            'callback_url': callback_url,
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            if result['status']:
                authorization_url = result['data']['authorization_url']
                logger.info("Payment initialization successful. Redirecting to Paystack.")
                return redirect(authorization_url)
            else:
                messages.error(request, f"Payment initialization failed: {result.get('message', 'Unknown error')}")
                logger.error(f"Payment initialization failed: {result.get('message', 'Unknown error')}")
        except requests.RequestException as e:
            messages.error(request, f"Network error occurred: {str(e)}")
            logger.error(f"Network error: {str(e)}")
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")
            logger.error(f"Unexpected error: {str(e)}")

    logger.warning("Payment initialization POST request missing.")
    return redirect('access_keys:purchase_access_key')



@require_GET
@csrf_exempt
def paystack_callback(request):
    """
    Handles the callback from Paystack after a successful payment.

   Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse indicating the success or failure of the payment.
    """

    reference = request.GET.get('reference')

    if not reference:
        logger.error("Payment reference not supplied.")
        return HttpResponse('Reference not supplied', status=400)

    url = f"{settings.PAYSTACK_SETTINGS.get('BASE_URL', 'https://api.paystack.co')}/transaction/verify/{reference}"
    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SETTINGS["SECRET_KEY"]}',
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        result = response.json()

        if result['status']:
            # Payment was successful
            amount = result['data']['amount'] / 100  # Convert from pesewas to cedis
            email = result['data']['customer']['email']

            if not email:
                logger.error("Email not found in payment verification.")
                return HttpResponse('Email not found', status=400)

            user = get_object_or_404(User, email=email)
            school = get_object_or_404(School, users=user)

            # Create access key
            procurement_date = timezone.now()
            expiry_date = procurement_date + timedelta(days=1)
            access_key = AccessKey.objects.create(
                school=school,
                key=generate_access_key(),
                status='active',
                assigned_to=user,
                procurement_date=procurement_date,
                expiry_date=expiry_date,
                price=amount,
            )

            # Log key creation
            KeyLog.objects.create(
                access_key=access_key,
                action=f'Access key {access_key.key} purchased for school {school.name}',
                user=user
            )

            # Send email notification
            subject = 'Access Key Purchase Successful'
            html_message = render_to_string('emails/access_key_purchase_success.html', {'user': user, 'access_key': access_key, 'school': school})
            plain_message = strip_tags(html_message)
            from_email = settings.DEFAULT_FROM_EMAIL
            to = user.email

            send_mail(subject, plain_message, from_email, [to], html_message=html_message)

            messages.success(request, 'Payment successful. Access key purchased.')
            logger.info("Payment verification successful. Access key created and email sent.")
            return redirect('school_dashboard')
        else:
            messages.error(request, 'Payment failed.')
            logger.error("Payment verification failed.")
            return redirect('school_dashboard')

    except requests.RequestException as e:
        logger.error(f"Error verifying payment: {str(e)}")
        return HttpResponse('Error verifying payment', status=500)

    logger.error("Payment verification failed.")
    return HttpResponse('Payment verification failed', status=400)

@login_required
@user_passes_test_with_403(is_admin)
@permission_required('users.can_revoke_access_key', raise_exception=True)
def revoke_access_key_view(request, key_id):
    """
    This view handles the revocation of an access key by an admin.

    Args:
        request: The HTTP request object.
        key_id: The ID of the access key to be revoked.

    Returns:
        If the revocation is successful, redirects to the admin dashboard.
        If the access key does not exist, an error message is displayed.
    """
    access_key = get_object_or_404(AccessKey, id=key_id)
    if request.method == 'POST':
        access_key.status = 'revoked'
        access_key.revoked_by = request.user
        access_key.revoked_on = timezone.now()
        access_key.save()

        # Log key revocation
        KeyLog.objects.create(
            access_key=access_key,
            action=f'Access key {access_key.key} revoked for school {access_key.school.name}',
            user=request.user,
        )

        messages.success(request, 'Access key revoked successfully.')
        logger.info(f"Access key {access_key.key} revoked by admin.")
        return redirect('admin_dashboard')

    context = common_context_data(request)
    context.update({
        'access_key': access_key,
    })
    logger.info("Rendering revoke access key page.")
    return render(request, 'access_keys/revoke_access_key.html', context)
