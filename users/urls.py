from django.urls import path
from . import views
from django.views.generic import TemplateView
from users import views as users_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', users_views.home, name='home'),  # Home page

    path('school-dashboard/', users_views.school_dashboard_view, name='school_dashboard'),  # School dashboard
    path('admin-dashboard/', users_views.admin_dashboard_view, name='admin_dashboard'),  # Admin dashboard

    path('register/', users_views.registration_options_view, name='register_options'),  # Registration options
    path('register/school/', users_views.register_view, {'user_type': 'school_personnel'}, name='register_school_personnel'),  # School personnel registration
    path('register/admin/', users_views.register_view, {'user_type': 'admin'}, name='register_admin'),  # Admin registration
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),  # Account activation
    path('registration_pending/', TemplateView.as_view(template_name='authentication/registration_pending.html'), name='registration_pending'),  # Registration pending page
    path('activation_success/', TemplateView.as_view(template_name='authentication/activation_success.html'), name='activation_success'),  # Activation success page
    path('activation_invalid/', TemplateView.as_view(template_name='authentication/activation_invalid.html'), name='activation_invalid'),  # Activation invalid page

    path('login/', users_views.login_view, name='login'),  # Login
    path('logout/', users_views.logout_view, name='logout'),  # Logout

    path('profile/', users_views.profile_view, name='profile'),  # Profile
    path('profile/complete/', users_views.complete_profile_view, name='complete_profile'),  # Complete profile
    path('profile/update/', users_views.update_profile_view, name='update_profile'),  # Update profile
    path('profile/billing-info/', users_views.billing_information_view, name='billing_information'),  # Billing information
    path('profile/billing-info/update/', users_views.update_billing_information_view, name='update_billing_info'),  # Update billing information

    # Password Reset URLs
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='authentication/password_reset_form.html'), name='password_reset'),  # Password reset
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='authentication/password_reset_done.html'), name='password_reset_done'),  # Password reset done
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='authentication/password_reset_confirm.html'), name='password_reset_confirm'),  # Password reset confirm
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='authentication/password_reset_complete.html'), name='password_reset_complete'),  # Password reset complete

    # Password Change URLs
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='authentication/password_change_form.html'), name='password_change'),  # Password change
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='authentication/password_change_done.html'), name='password_change_done'),  # Password change done
]
