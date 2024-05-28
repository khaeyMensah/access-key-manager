from django.urls import path
from access_keys import api_views, views

app_name = 'access_keys'  # This sets the namespace for the app

urlpatterns = [
    path('', views.access_keys, name='list'),
    path('revoke/<int:key_id>/', views.revoke_key, name='revoke_key'),
    path('verify_key/<str:school_email>/', api_views.verify_key, name='verify_key'),
]
