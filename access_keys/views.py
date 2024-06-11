import random
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.utils import timezone

from access_keys.models import AccessKey, KeyLog
from users.contexts import common_context_data
from users.forms import BillingInformationForm
from users.models import School
from .utils import generate_access_key


# Create your views here.
@login_required
@user_passes_test(lambda u: u.is_school_personnel)
def purchase_access_key_view(request):
    school = get_object_or_404(School, users=request.user)
    active_keys = school.access_keys.filter(status='active')
    
    if active_keys.exists():
        messages.error(request, 'You already have an active access key.')
        return redirect('school_dashboard')
    
    billing_info = getattr(request.user, 'billing_information', None)


    if request.method == 'POST':
        form = BillingInformationForm(request.POST, instance=billing_info)
        if form.is_valid():
            if form.cleaned_data.get('confirm_purchase'):
                billing_info = form.save(commit=False)
                billing_info.user = request.user
                billing_info.save()

                payment_successful = mock_payment_process(billing_info)

                if payment_successful:
                    procurement_date = timezone.now().date()
                    expiry_date = timezone.now().date() + timezone.timedelta(days=1)
                    access_key = AccessKey(
                        school=school,
                        key=generate_access_key(),
                        status='active',
                        assigned_to=request.user,
                        procurement_date=procurement_date,
                        expiry_date=expiry_date,
                        price=settings.ACCESS_KEY_PRICE,
                    )
                    access_key.save()

                    KeyLog.objects.create(
                        access_key=access_key,
                        action=f'Access key {access_key.key} purchased for school {school.name}',
                        user=request.user
                    )

                    messages.success(request, 'Access key purchased successfully.')
                    return redirect('school_dashboard')
                else:
                    messages.error(request, 'Payment failed. Please try again.')
            else:
                messages.error(request, 'You must confirm the purchase to proceed.')    
        else:
            messages.error(request, 'Please provide valid billing information.')
    else:
        form = BillingInformationForm(instance=billing_info)

    context = common_context_data(request)
    context.update({
        'form': form,
        'school': school,
        'access_key_price': settings.ACCESS_KEY_PRICE,
    })
    return render(request, 'access_keys/purchase_access_key.html', context)


@login_required
@user_passes_test(lambda u: u.is_admin)
def revoke_access_key_view(request, key_id):
    access_key = get_object_or_404(AccessKey, id=key_id)
    if request.method == 'POST':
        access_key.status = 'revoked'
        access_key.revoked_by = request.user
        access_key.revoked_on = timezone.now()
        access_key.save()

        KeyLog.objects.create(
            access_key = access_key,
            action=f'Access key {access_key.key} revoked for school {access_key.school.name}',
            user=request.user
        )
        messages.success(request, 'Access key revoked successfully.')
        return redirect('admin_dashboard')
    
    context = common_context_data(request)
    context.update ({
        'access_key': access_key
    })
    return render(request, 'access_keys/revoke_access_key.html', context)
    

def mock_payment_process(billing_info):
    """
    Mock payment processing function.
    Simulates a successful or failed payment based on a random boolean value.
    """
    payment_method = billing_info.payment_method

    # Simulate different payment scenarios based on the payment method
    if payment_method == "Card":
        # Simulate a successful payment for card payments 80% of the time
        payment_successful = random.random() < 0.8
    elif payment_method == "MTN":
        # Simulate a successful payment for mobile money payments 90% of the time
        payment_successful = random.random() < 0.9
    else:
        # For any other payment method, simulate a failed payment
        payment_successful = False

    return payment_successful
