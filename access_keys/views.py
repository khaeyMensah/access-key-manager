from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
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
from users.helpers import is_admin, is_school_personnel
from users.models import School, User
from .utils import generate_access_key



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
        form = BillingInformationForm(request.POST, instance=billing_info, user=request.user)
        if form.is_valid():
            if form.cleaned_data.get('confirm_purchase'):
                billing_info = form.save(commit=False)
                billing_info.user = request.user
                billing_info.save()
                request.POST = request.POST.copy()
                request.POST['user_id'] = request.user.id
                return redirect('access_keys:initialize_payment')

            else:
                messages.error(request, 'You must confirm the purchase to proceed.')
        else:
            print("Form errors:", form.errors)  # Debugging
            messages.error(request, 'Please provide valid billing information.')
    else:
        form = BillingInformationForm(instance=billing_info, user=request.user)

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
            return redirect('access_keys:purchase_access_key')

        # Retrieve user_id from the form data
        user_id = request.POST.get('user_id')

        base_url = settings.PAYSTACK_SETTINGS.get('BASE_URL', 'https://api.paystack.co')
        callback_url = f"{settings.PAYSTACK_SETTINGS['CALLBACK_URL']}"

        url = f"{base_url}/transaction/initialize"
        headers = {
            'Authorization': f'Bearer {settings.PAYSTACK_SETTINGS["SECRET_KEY"]}',
            'Content-Type': 'application/json',
        }
        data = {
            'email': billing_info.email,
            'amount': int(settings.ACCESS_KEY_PRICE * 100),
            'currency': 'GHS',
            'callback_url': callback_url,
            'metadata': {
                'user_id': user_id,
            },
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            if result['status']:
                authorization_url = result['data']['authorization_url']
                return redirect(authorization_url)
            else:
                messages.error(request, f"Payment initialization failed: {result.get('message', 'Unknown error')}")
        except requests.RequestException as e:
            messages.error(request, f"Network error occurred: {str(e)}")
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")

    return redirect('access_keys:purchase_access_key')



@require_GET
@csrf_exempt
def paystack_callback(request):
    """
    This view handles the callback from Paystack after a successful payment for purchasing an access key.

    Args:
        request (HttpRequest): The HTTP request object containing the reference parameter.

    Returns:
        HttpResponse: A response containing a success or error message based on the payment status.

    Raises:
        Http400Response: If the reference parameter is not supplied in the request.
        Http500Response: If a network error or unexpected error occurs during the payment verification process.

    The function first checks if the reference parameter is supplied in the request. If not, it returns an Http400Response with a message indicating that the reference parameter is missing.

    If the reference parameter is supplied, the function constructs the URL for verifying the payment using the reference parameter and the Paystack settings. It then sends a GET request to the Paystack API with the necessary headers and retrieves the payment verification result.

    If the payment verification result is successful, the function extracts the user ID from the transaction metadata, retrieves the corresponding User and School objects, creates a new AccessKey object, logs the action in the KeyLog model, and sends an email notification to the user. Finally, it returns an HttpResponse with a success message and redirects to the school dashboard.

    If the payment verification result is not successful, the function returns an HttpResponse with an error message and redirects to the school dashboard.

    If any network or unexpected errors occur during the payment verification process, the function returns an Http500Response with a message indicating the nature of the error.
    """

    reference = request.GET.get('reference')

    if not reference:
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
            amount = result['data']['amount'] / 100
            metadata = result['data'].get('metadata', {})
            user_id = metadata.get('custom_fields', [{}])[0].get('value')  # Correct extraction of user_id
            
            if not user_id:
                return HttpResponse('User ID not found in transaction metadata', status=400)

            try:
                user = get_object_or_404(User, id=user_id)
            except User.DoesNotExist:
                return HttpResponse(f'User with ID {user_id} not found in database', status=400)
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
            
            # Send email notification
            subject = 'Access Key Purchase Successful'
            html_message = render_to_string('emails/access_key_purchase_success.html', {'user': user, 'access_key': access_key, 'school': school})
            plain_message = strip_tags(html_message)
            from_email = settings.DEFAULT_FROM_EMAIL
            to = user.email

            send_mail(subject, plain_message, from_email, [to], html_message=html_message)


            messages.success(request, 'Payment successful. Access key purchased.')
            return redirect('school_dashboard')
        else:
            messages.error(request, 'Payment failed.')
            return redirect('school_dashboard')

    except requests.RequestException as e:
        return HttpResponse(f'Network error: {str(e)}', status=500)
    except Exception as e:
        return HttpResponse(f'An unexpected error occurred: {str(e)}', status=500)


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

