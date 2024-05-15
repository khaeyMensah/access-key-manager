from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Role, BillingInformation

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Role)
admin.site.register(BillingInformation)