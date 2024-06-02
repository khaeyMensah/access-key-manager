from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.utils import timezone

from access_keys.models import AccessKey, KeyLog, School
from users.forms import BillingInformationForm
from .utils import generate_access_key

# Create your views here.
@login_required
@user_passes_test(lambda u: u.is_school_personnel)
def purchase_access_key_view(request):
    user = request.user
    school = user.school

    if not school:
        messages.error(request, 'You need to complete your profile and assign a school before purchasing an access key.')
        return redirect('profile_update') 

    active_keys = school.access_keys.filter(status='active')
    
    if active_keys.exists():
        messages.error(request, 'You already have an active access key.')
        return redirect('school_dashboard')
    
    if request.method == 'POST':
        form = BillingInformationForm(request.POST, instance=request.user.billing_information)
        if form.is_valid():
            billing_info = form.save(commit=False)
            billing_info.user = request.user
            billing_info.save()

            access_key = AccessKey(
                school=school,
                key=generate_access_key(),
                status='active',
                assigned_to=user,
                procurement_date=timezone.now().date(),
                expiry_date=timezone.now().date() + timezone.timedelta(days=1),
            )
            access_key.save()

            KeyLog.objects.create(
                action=f'Access key {access_key.key} purchased for school {school.name}',
                user=user
            )

            messages.success(request, 'Access key purchased successfully.')
            return redirect('school_dashboard')
        else:
            messages.error(request, 'Please provide valid billing information.')

    else:
        form = BillingInformationForm(instance=request.user.billing_information)

    context = {
        'form': form,
        'school': school,
    }
    return render(request, 'access_keys/purchase_access_key.html', context)


@login_required
@user_passes_test(lambda u: u.is_admin)
def revoke_access_key_view(request, access_key_id):
    access_key = get_object_or_404(AccessKey, id=access_key_id)
    if request.method == 'POST':
        access_key.status = 'revoked'
        access_key.save()
        AccessKey.objects.create(
            key = access_key.key_value,
            school = access_key.school,
            revoked_by = request.user,
            revoked_on = timezone.now()
        )

        KeyLog.objects.create(
            action=f'Access key {access_key.key} revoked for school {access_key.school.name}',
            user=request.user
        )
        messages.success(request, 'Access key revoked successfully.')
        return redirect('admin_dashboard')
    return render(request, 'access_keys/revoke_access_key.html', {'access_key': access_key})
    