from django.shortcuts import render, redirect
from .models import AccessKey
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def access_keys(request):
    keys = AccessKey.objects.filter(user=request.user)
    return render(request, 'access_keys/list.html', {'keys': keys})

@login_required
def revoke_key(request, key_id):
    key = AccessKey.objects.get(id=key_id)
    if request.user.has_perm('access_keys.revoke_accesskey') and key.assigned_to == request.user:
        key.status = 'revoked'
        key.save()
    return redirect('access_keys:list')