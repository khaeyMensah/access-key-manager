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
        
        
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

        
class BillingInformationForm(forms.ModelForm):
    email = forms.EmailField()
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
                raise forms.ValidationError('Card number is required.')
            if not card_expiry:
                raise forms.ValidationError('Card expiry date is required.')
            if not card_cvv:
                raise forms.ValidationError('Card CVV is required.')

        elif payment_method == "MTN":
            if not mobile_money_number:
                raise forms.ValidationError('MOMO number is required.')

        return cleaned_data
        


# class BillingInformationForm(forms.ModelForm):
#     email = forms.EmailField()
#     class Meta:
#         model = BillingInformation
#         fields = ['email', 'payment_method', 'mobile_money_number', 'card_number', 'card_expiry', 'card_cvv']

        # def __init__(self, *args, **kwargs):
        #     super().__init__(*args, **kwargs)
        #     self.fields['mobile_money_number'].required = False
        #     self.fields['card_number'].required = False
            
        # def clean(self):
        #     cleaned_data = super().clean()
        #     email = cleaned_data.get('email')
        #     payment_method = cleaned_data.get('payment_method')
        #     mobile_money_number = cleaned_data.get('mobile_money_number')
        #     card_number = cleaned_data.get('card_number')
        #     card_expiry = cleaned_data.get('card_expiry')
        #     card_cvv = cleaned_data.get('card_cvv')
            
        #     if not email:
        #         raise forms.ValidationError('Please provide an email address.')
            
        #     if payment_method == "Card":
        #         if not card_number:
        #             raise forms.ValidationError('Card number is required.')
        #         if not card_expiry:
        #             raise forms.ValidationError('Card expiry date is required.')
        #         if not card_cvv:
        #             raise forms.ValidationError('Card CVV is required.')

        #     elif payment_method == "MTN":
        #         if not mobile_money_number:
        #             raise forms.ValidationError('MTN number is required.')

        #     return cleaned_data




        # if payment_method == 'MTN':
        #     if not mobile_money_number:
        #         raise forms.ValidationError('Please provide a mobile money number.')
        # elif payment_method == 'Card':
        #     if not card_number or not card_expiry or not card_cvv:
        #         raise forms.ValidationError('Please provide card details.')

        # return cleaned_data

