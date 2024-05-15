from django.contrib import admin
from .models import AccessKey, School, RevokedAccessKey, AuditLog

# Register your models here.
admin.site.register(AccessKey)
admin.site.register(School)
admin.site.register(RevokedAccessKey)
admin.site.register(AuditLog)