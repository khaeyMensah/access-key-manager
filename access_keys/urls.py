from django.urls import path
from access_keys import views


urlpatterns = [
    path('', views.access_keys, name='access keys'),
]
