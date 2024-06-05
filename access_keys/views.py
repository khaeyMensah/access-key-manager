from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.utils import timezone

from access_keys.models import AccessKey, KeyLog
from users.forms import BillingInformationForm
from users.models import BillingInformation, School
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

            # Assume process_payment is a function that processes the payment
            # payment_successful = process_payment(billing_info)

            procurement_date=timezone.now().date()
            expiry_date=timezone.now().date() + timezone.timedelta(days=1)
            access_key = AccessKey(
                school=school,
                key=generate_access_key(),
                status='active',
                assigned_to=request.user,
                procurement_date=procurement_date,
                expiry_date=expiry_date,
                price = 100,
            )
            access_key.save()

            KeyLog.objects.create(
                access_key = access_key,
                action=f'Access key {access_key.key} purchased for school {school.name}',
                user=request.user
            )

            messages.success(request, 'Access key purchased successfully.')
            return redirect('school_dashboard')
        else:
            messages.error(request, 'Please provide valid billing information.')

    else:
        form = BillingInformationForm(instance=billing_info)

    context = {
        'form': form,
        'school': school,
    }
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
    return render(request, 'access_keys/revoke_access_key.html', {'access_key': access_key})
    
