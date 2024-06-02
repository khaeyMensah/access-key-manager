from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login as auth_login, logout
from django.urls import reverse_lazy
from access_keys.models import AccessKey, KeyLog, School
from django.contrib import messages
from users.models import BillingInformation, User
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView

from users.forms import AdminRegistrationForm, BillingInformationForm, RegistrationForm, LoginForm

# Create your views here.
def home(request):
    return render(request, 'users/home.html')


def admin_register_view(request):
    if request.method == "POST":
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_admin = True
            user.save()
            messages.success(request, 'Registration successful.')
            auth_login(request, user)
            return redirect('complete_profile')
    else:
        form = AdminRegistrationForm()
    return render(request, 'accounts/admin_register.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, 'Login successful.')
            if user.is_admin:
                return redirect('admin_dashboard')
            else:
                return redirect('school_dashboard')
            
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_school_personnel)
def school_dashboard_view(request):
    if not request.user.is_school_personnel:
        return redirect('access_denied')    
    try:
        school = get_object_or_404(School, users=request.user)
        # access_keys = school.access_Keys.objects.order_by('-date_of_procurement')
        access_keys = school.access_keys.all()
        
        context = {
            'school': school,
            'access_keys': access_keys,
        }
        return render(request, 'users/school_dashboard.html', context)
    except School.DoesNotExist:
        messages.error(request, 'No School associated with your account.')
        return redirect('home')
        
        
@login_required
@user_passes_test(lambda u: u.is_admin)
def admin_dashboard_view(request):
    if not request.user.is_admin:
        return redirect('access_denied')

    # access_keys = school.access_keys.all()
    access_keys = AccessKey.objects.order_by('-date_of_procurement')
    key_logs = KeyLog.objects.order_by('-timestamp')
    
    context = {
        'access_keys': access_keys,
        'key_logs': key_logs,    
    }
    return render(request, 'users/admin_dashboard.html', context)


def register_view(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_school_personnel = True
            user.save()
            messages.success(request, 'Registration successful.')
            auth_login(request, user)
            return redirect('complete_profile')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Logout successful.')
    return redirect('home')


@method_decorator(login_required, name='dispatch')
class ProfileUpdateView(UpdateView):
    model = User
    fields = ('first_name', 'last_name', 'email', 'school')
    template_name = 'accounts/complete_profile.html'
    success_url = reverse_lazy('home')

    def get_object(self):
        return self.request.user

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if not self.request.user.school:
            form.fields['school'] = self.model._meta.get_field('school').formfield()
        return form

    def form_valid(self, form):
        if not self.request.user.school:
            form.instance.school = form.cleaned_data.get('school')
        return super().form_valid(form)

    
    
@login_required
def billing_information_view(request):
    try:
        billing_info = request.user.billing_information
    except BillingInformation.DoesNotExist:
        billing_info = None

    if request.method == 'POST':
        form = BillingInformationForm(request.POST, instance=billing_info)
        if form.is_valid():
            billing_info = form.save(commit=False)
            billing_info.user = request.user
            billing_info.save()
            messages.success(request, 'Billing information updated successfully.')
            return redirect('school_dashboard')
    else:
        form = BillingInformationForm(instance=billing_info)

    context = {
        'form': form,
    }
    return render(request, 'accounts/billing_info.html', context)

@login_required
def update_billing_information_view(request):
    return billing_information_view(request)
