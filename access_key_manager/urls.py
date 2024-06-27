"""
URL configuration for access_key_manager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from users import views as users_views 


urlpatterns = [
    path('admin/', admin.site.urls),  # Admin site URL
    path('accounts/', include('users.urls')),  # User-related URLs
    path('access-keys/', include('access_keys.urls', namespace="access_keys")),  # Access key-related URLs
    path('', include('users.urls')),  # Root URL, pointing to user-related views
]

handler403 = 'users.views.custom_permission_denied'