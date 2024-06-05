from django.http import JsonResponse
from django.views.decorators.http import require_GET
from users.models import School

@require_GET
def check_access_key_status_view(request):
    school_email = request.GET.get('school_email')
    if not school_email:
        return JsonResponse({'error': 'school_email parameter is required.'}, status=400)

    try:
        school = School.objects.get(user__email=school_email)
        active_key = school.access_keys.filter(status='active').first()
        if active_key:
            data = {
                'key': active_key.key,
                'status': active_key.status,
                'procurement_date': active_key.procurement_date,
                'expiry_date': active_key.expiry_date,
            }
            return JsonResponse(data, status=200)
        else:
            return JsonResponse({'error': 'No active access key found.'}, status=404)
    except School.DoesNotExist:
        return JsonResponse({'error': 'School not found.'}, status=404)