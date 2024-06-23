from django.contrib import admin
from .models import AccessKey, School, KeyLog

# Register your models here.
admin.site.register(AccessKey)
admin.site.register(School)
admin.site.register(KeyLog)

