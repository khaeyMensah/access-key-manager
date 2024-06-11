from access_keys.models import AccessKey
from users.models import School


def common_context_data(request):
    total_schools =  0
    total_active_keys =  0
    total_revoked_keys =  0
    total_expired_keys =  0
    active_key =  None
    expired_keys_count =  0
    revoked_keys_count =  0
    keys_purchased_count = 0

    
    total_schools = School.objects.count()
    total_active_keys = AccessKey.objects.filter(status='active').count()
    total_revoked_keys = AccessKey.objects.filter(status='revoked').count()
    total_expired_keys = AccessKey.objects.filter(status='expired').count()
    
    context = {
        'total_schools': total_schools,
        'total_active_keys': total_active_keys,
        'total_revoked_keys': total_revoked_keys,
        'total_expired_keys': total_expired_keys,
        'total_keys_purchased': total_active_keys + total_revoked_keys + total_expired_keys,
    }

    if request.user.is_authenticated and request.user.is_school_personnel and request.user.school:
        school = request.user.school
        active_key = school.access_keys.filter(status='active').first()
        expired_keys_count = school.access_keys.filter(status='expired').count()
        revoked_keys_count = school.access_keys.filter(status='revoked').count()
        keys_purchased_count = school.access_keys.count()
            
        context.update({
            'active_key': active_key,
            'expired_keys_count': expired_keys_count,
            'revoked_keys_count': revoked_keys_count,
            'keys_purchased_count': keys_purchased_count,
        })
            
    return context
            