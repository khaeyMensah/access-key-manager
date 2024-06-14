from django import forms
from users.models import BillingInformation, School, User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class RegistrationForm(UserCreationForm):
    email = forms.CharField(max_length=254, required=True, widget=forms.EmailInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.is_active = False
        if commit:
            user.save()
        return user

class LoginForm(AuthenticationForm):
    class Meta:
        model = User

class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    school = forms.ModelChoiceField(queryset=School.objects.all(), required=False, empty_label="Select a school")
    staff_id = forms.CharField(required=False, label='Staff ID')

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'school', 'staff_id']

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        if not email:
            self.add_error('email', 'Please provide an email address.')
        return cleaned_data

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class BillingInformationForm(forms.ModelForm):
    card_expiry = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    confirm_purchase = forms.BooleanField(required=True, initial=False, label='Confirm purchase')

    class Meta:
        model = BillingInformation
        fields = ['payment_method', 'mobile_money_number', 'card_number', 'card_expiry', 'card_cvv']

    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        mobile_money_number = cleaned_data.get('mobile_money_number')
        card_number = cleaned_data.get('card_number')
        card_expiry = cleaned_data.get('card_expiry')
        card_cvv = cleaned_data.get('card_cvv')

        if payment_method == "Card":
            if not card_number:
                self.add_error('card_number', 'Card number is required.')
            if not card_expiry:
                self.add_error('card_expiry', 'Card expiry date is required.')
            if not card_cvv:
                self.add_error('card_cvv', 'Card CVV is required.')
            if mobile_money_number:
                self.add_error('mobile_money_number', 'MOMO number is not required for card payment.')

        elif payment_method == "MTN":
            if not mobile_money_number:
                self.add_error('mobile_money_number', 'MOMO number is required.')
            if card_number or card_expiry or card_cvv:
                self.add_error(None, 'Credit card details are not required for MOMO payment.')

        return cleaned_data

class UpdateBillingInformationForm(forms.ModelForm):
    card_expiry = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)

    class Meta:
        model = BillingInformation
        fields = ['payment_method', 'mobile_money_number', 'card_number', 'card_expiry', 'card_cvv']

    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        mobile_money_number = cleaned_data.get('mobile_money_number')
        card_number = cleaned_data.get('card_number')
        card_expiry = cleaned_data.get('card_expiry')
        card_cvv = cleaned_data.get('card_cvv')

        if payment_method == "Card":
            if not card_number:
                self.add_error('card_number', 'Card number is required.')
            if not card_expiry:
                self.add_error('card_expiry', 'Card expiry date is required.')
            if not card_cvv:
                self.add_error('card_cvv', 'Card CVV is required.')
            if mobile_money_number:
                self.add_error('mobile_money_number', 'MOMO number is not required for card payment.')

        elif payment_method == "MTN":
            if not mobile_money_number:
                self.add_error('mobile_money_number', 'MOMO number is required.')
            if card_number or card_expiry or card_cvv:
                self.add_error(None, 'Credit card details are not required for MOMO payment.')

        return cleaned_data