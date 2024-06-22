from django.urls import path
from access_keys import api_views, views

app_name = 'access_keys'

urlpatterns = [
    path('purchase-access-key/', views.purchase_access_key_view, name='purchase_access_key'),
    path('initialize-payment/', views.initialize_payment, name='initialize_payment'),
    path('paystack/callback/', views.paystack_callback, name='paystack_callback'),
    path('access-keys/revoke/<int:key_id>/', views.revoke_access_key_view, name='revoke_access_key'),
    path('api/status/<str:email>/', api_views.check_access_key_status_view, name='key_status'),
]
 