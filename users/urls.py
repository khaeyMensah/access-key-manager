from django.urls import path
from users import views as users_views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', users_views.home, name='home'),
    path('school-dashboard/', users_views.school_dashboard_view, name='school_dashboard'),
    path('admin-dashboard/', users_views.admin_dashboard_view, name='admin_dashboard'),
    path('register/', users_views.register_view, name='register'),
    path('admin-register/', users_views.admin_register_view, name='admin_register'),
    path('login/', users_views.login_view, name='login'),
    path('logout/', users_views.logout_view, name='logout'),
    
    path('profile/', users_views.profile_view, name='profile'),
    path('profile/complete/', users_views.profile_complete_view, name='complete_profile'),
    path('profile/update/', users_views.update_profile_view, name='update_profile'),
    path('profile/billing-info/', users_views.billing_information_view, name='billing_information'),
    path('profile/billing-info/confirm/', users_views.confirm_billing_information_view, name='confirm_billing_info'),
    path('profile/billing-info/update', users_views.update_billing_information_view, name='update_billing_info'),

    # Password Reset URLs
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='authentication/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='authentication/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='authentication/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='authentication/password_reset_complete.html'), name='password_reset_complete'),
    
    # Password Change URLs
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='authentication/password_change_form.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='authentication/password_change_done.html'), name='password_change_done'),
]
