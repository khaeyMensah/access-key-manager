from django.urls import path, re_path
from users import views as users_views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', users_views.home, name='home'),
    path('register/', users_views.register, name='register'),
    path('login/', users_views.login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('reset/', users_views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('reset/<uidb64>/<token>/', users_views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    
    # path('reset/', 
    #     auth_views.PasswordResetView.as_view(
    #         template_name='authentication/password_reset.html',
    #         email_template_name='authentication/password_reset_email.html',
    #         subject_template_name='authentication/password_reset_subject.txt'
    #     ), 
    #     name='password_reset'),
    # path('reset/done/', 
    #     auth_views.PasswordResetDoneView.as_view(template_name='authentication/password_reset_done.html'), 
    #     name='password_reset_done'),
    # re_path(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', 
    #     auth_views.PasswordResetConfirmView.as_view(template_name='authentication/password_reset_confirm.html'), 
    #     name='password_reset_confirm'),
    # path('reset/complete/', 
    #     auth_views.PasswordResetCompleteView.as_view(template_name='authentication/password_reset_complete.html'), 
    #     name='password_reset_complete'),

    # path('settings/password/', auth_views.PasswordChangeView.as_view(template_name='authentication/password_change.html'),
    #     name='password_change'),
    # path('settings/password/done/', auth_views.PasswordChangeDoneView.as_view(template_name='authentication/password_change_done.html'),
    #     name='password_change_done'),
]
