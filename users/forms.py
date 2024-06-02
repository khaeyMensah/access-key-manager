from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from users.models import BillingInformation, User


class RegistrationForm(UserCreationForm):
    email = forms.CharField(max_length=254, required=True, widget=forms.EmailInput())
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
class AdminRegistrationForm(UserCreationForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class LoginForm(AuthenticationForm):
    class Meta:
        model = User
        
        
class BillingInformationForm(forms.ModelForm):
    email = forms.EmailField()
    class Meta:
        model = BillingInformation
        fields = ['email', 'payment_method', 'mobile_money_number', 'card_number', 'card_expiry', 'card_cvv']

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['mobile_money_number'].required = False
            self.fields['card_number'].required = False
            
        email = forms.EmailField(required=True)
        payment_method = forms.ChoiceField(choices=BillingInformation.PAYMENT_METHODS)
        mobile_money_number = forms.CharField(max_length=15, required=False)
        card_number = forms.CharField(max_length=16, required=False)
        card_expiry = forms.CharField(max_length=5, required=False)
        card_cvv = forms.CharField(max_length=3, required=False)
        price = forms.DecimalField(max_digits=8, decimal_places=2)
            
        def clean(self):
            cleaned_data = super().clean()
            payment_method = cleaned_data.get('payment_method')
            
            if payment_method == "Card":
                if not cleaned_data.get("card_number"):
                    self.add_error('card_number', 'Card number is required.')
                if not cleaned_data.get("card_expiry"):
                    self.add_error('card_expiry', 'Card expiry date is required.')
                if not cleaned_data.get("card_cvv"):
                    self.add_error('card_cvv', 'Card CVV is required.')

            elif payment_method == "MTN":
                if not cleaned_data.get("mobile_money_number"):
                    self.add_error('mobile_money_number', 'MTN number is required.')

            return cleaned_data

