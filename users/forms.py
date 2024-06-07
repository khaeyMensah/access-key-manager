from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from users.models import BillingInformation, User


class RegistrationForm(UserCreationForm):
    email = forms.CharField(max_length=254, required=True, widget=forms.EmailInput())
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        

class LoginForm(AuthenticationForm):
    class Meta:
        model = User
        

class UserCompleteForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'school']

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        if not email:
            raise forms.ValidationError('Please provide an email address.')
        return cleaned_data
        
        
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

        
class BillingInformationForm(forms.ModelForm):
    email = forms.EmailField()
    card_expiry = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)

    class Meta:
        model = BillingInformation
        fields = ['email', 'payment_method', 'mobile_money_number', 'card_number', 'card_expiry', 'card_cvv']

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        payment_method = cleaned_data.get('payment_method')
        mobile_money_number = cleaned_data.get('mobile_money_number')
        card_number = cleaned_data.get('card_number')
        card_expiry = cleaned_data.get('card_expiry')
        card_cvv = cleaned_data.get('card_cvv')

        if not email:
            raise forms.ValidationError('Please provide an email address.')

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
