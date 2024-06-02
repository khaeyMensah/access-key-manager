# from django import forms
# from access_keys.models import AccessKey

# class PurchaseAccessKeyForm(forms.ModelForm):
#     class Meta:
#         model = AccessKey
#         fields = ['expiry_date', 'price']

#     def clean(self):
#         cleaned_data = super().clean()
#         expiry_date = cleaned_data.get('expiry_date')
#         price = cleaned_data.get('price')

#         # Add validation logic for expiry_date and price
#         # ...

#         return cleaned_data
    