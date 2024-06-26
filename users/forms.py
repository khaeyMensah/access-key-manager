import logging
import re
from django.core.exceptions import ValidationError
from django import forms
from users.models import BillingInformation, School, User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


logger = logging.getLogger(__name__)

class RegistrationForm(UserCreationForm):
    """
    A form for handling user registration.

    Attributes:
        email (forms.CharField): A field for the user's email address.

    Methods:
        save(self, commit=True): Saves the user object with the provided email and sets the user's is_active flag to False.
    """
    email = forms.CharField(max_length=254, required=True, widget=forms.EmailInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


    def clean_email(self):
        """
    
        Validates the email field and raises a ValidationError if it's already registered.

        Args:
            self (RegistrationForm): An instance of the RegistrationForm class.

        Returns:
            email (str): The validated email address.

        Raises:
            ValidationError: If the email address is already registered.
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            logger.warning(f"Attempted registration with existing email: {email}")
            raise ValidationError("This email is already registered.")
        return email


    def save(self, commit=True):
        """
        Saves the user instance with the provided email and sets the user's is_active flag to False.

        Args:
            commit (bool, optional): A boolean value indicating whether the user instance should be saved to the database. Defaults to True.

        Returns:
            User: The saved user instance.
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.is_active = False
        if commit:
            user.save()
            logger.info(f"New user registered with email: {user.email}")
        return user


class LoginForm(AuthenticationForm):
    """
    A form for handling user login.

    Attributes:
        Meta (class): A class for meta-information related to the form.
    """
    class Meta:
        model = User


class ProfileForm(forms.ModelForm):
    """
    A form for handling user profile information.

    Attributes:
        first_name (forms.CharField): A field for the user's first name.
        last_name (forms.CharField): A field for the user's last name.
        email (forms.EmailField): A field for the user's email address.
        school (forms.ModelChoiceField): A field for selecting a school.
        staff_id (forms.CharField): A field for the user's staff ID.

    Methods:
        __init__(self, *args, **kwargs): Initializes the ProfileForm with the provided arguments.
        clean(self): Validates the form data and raises a ValidationError if any field fails validation.
        clean_email(self): Validates the email field and raises a ValidationError if it's empty.
        clean_school(self): Validates the school field and raises a ValidationError if it's empty.
        save(self, commit=True): Saves the user instance with the provided profile information and sets the user's is_active flag to False.
    """
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    school = forms.ModelChoiceField(queryset=School.objects.all(), required=False, empty_label="Select a school")
    staff_id = forms.CharField(required=False, label='Staff ID')

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'school', 'staff_id']

    def clean(self):
        """
        Validates the form data and raises a ValidationError if any field fails validation.

        Args:
            self: An instance of ProfileForm.

        Returns:
            cleaned_data: A dictionary containing the validated form data.

        Raises:
            ValidationError: If any field fails validation.
        """
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        if not email:
            self.add_error('email', 'Please provide an email address.')
            logger.error("Profile update failed due to missing email address")
        return cleaned_data


class ProfileUpdateForm(forms.ModelForm):
    """
    Form for updating user profile with basic fields.
    """

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']


class BillingInformationForm(forms.ModelForm):
    """
    A form for handling billing information during purchase.

    Attributes:
        payment_method (forms.ChoiceField): A field for selecting a payment method.
        mobile_money_number (forms.CharField): A field for the user's mobile money number.
        card_number (forms.CharField): A field for the user's credit card number.
        card_expiry (forms.CharField): A field for the user's credit card expiry date.
        card_cvv (forms.CharField): A field for the user's credit card CVV.
        confirm_purchase (forms.BooleanField): A field for confirming the purchase.

    Methods:
        __init__(self, *args, **kwargs): Initializes the form with the provided arguments.
        clean(self): Validates the form data and raises a ValidationError if any field fails validation.
        clean_card_expiry(self): Validates the credit card expiry date and raises a ValidationError if it's empty or not in the correct format.

    """
    email = forms.EmailField(required=True)
    payment_method = forms.ChoiceField(choices=[('', 'Select a payment method')] + BillingInformation.PAYMENT_METHODS, required=True, label='Payment Method')
    mobile_money_number = forms.CharField(required=False, label='Mobile Money Number')
    card_number = forms.CharField(required=False, label='Card Number')
    card_expiry = forms.CharField(required=False, label='Card Expiry', widget=forms.TextInput(attrs={'placeholder': 'mm/yy'}))
    card_cvv = forms.CharField(required=False, label='Card CVV')
    confirm_purchase = forms.BooleanField(required=True, initial=False, label='Confirm purchase')
    
    class Meta:
        model = BillingInformation
        fields = ['email', 'payment_method', 'mobile_money_number', 'card_number', 'card_expiry', 'card_cvv']

    def __init__(self, *args, **kwargs):
        """
        Initializes the form with the provided arguments and sets the initial email value if a user object is provided.

        Parameters:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

        Keyword Arguments:
        user (User): An instance of the User model. If provided, the email field will be initialized with the user's email.

        Returns:
        None
        """
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and 'email' not in self.initial:
            self.initial['email'] = user.email

    def clean_card_expiry(self):
        """
        Validates the credit card expiry date and raises a ValidationError if it's empty or not in the correct format.

        Args:
            self: An instance of BillingInformationForm.

        Returns:
            card_expiry (str): The validated credit card expiry date.

        Raises:
            ValidationError: If the credit card expiry date is empty or not in the correct format.

        """
        card_expiry = self.cleaned_data.get('card_expiry')
        if card_expiry and not re.match(r'^(0[1-9]|1[0-2])\/\d{2}$', card_expiry):
            logger.error(f"Invalid card expiry date format: {card_expiry}")
            raise forms.ValidationError('Card expiry must be in mm/yy format.')
        return card_expiry
    
    def clean_mobile_money_number(self):
        """
        Validates the mobile money number field and raises a ValidationError if it's empty or not in the correct format.

        Args:
        self (BillingInformationForm): An instance of the BillingInformationForm class.

        Returns:
        mobile_money_number (str): The validated mobile money number.

        Raises:
        ValidationError: If the mobile money number is empty or not in the correct format.

        """
        mobile_money_number = self.cleaned_data.get('mobile_money_number')
        if mobile_money_number and not re.match(r'^\d{10}$', mobile_money_number):
            logger.error(f"Invalid mobile money number format: {mobile_money_number}")
            raise forms.ValidationError('Mobile Money Number must be 10 digits.')
        return mobile_money_number

    def clean(self):
        """
        Validates the form data and raises a ValidationError if any field fails validation.

        Args:
            self: An instance of BillingInformationForm.

        Returns:
            cleaned_data (dict): A dictionary containing the validated form data.

        Raises:
            ValidationError: If any field fails validation.

        """
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        mobile_money_number = cleaned_data.get('mobile_money_number')
        card_number = cleaned_data.get('card_number')
        card_expiry = cleaned_data.get('card_expiry')
        card_cvv = cleaned_data.get('card_cvv')

        if payment_method == "card":
            if not card_number:
                self.add_error('card_number', 'Card number is required.')
                logger.error("Card payment method selected but card number is missing")
            if not card_expiry:
                self.add_error('card_expiry', 'Card expiry date is required.')
                logger.error("Card payment method selected but card expiry date is missing")
            if not card_cvv:
                self.add_error('card_cvv', 'Card CVV is required.')
                logger.error("Card payment method selected but card CVV is missing")
            if mobile_money_number:
                self.add_error('mobile_money_number', 'MOMO number is not required for card payment.')
                logger.error("Mobile money number provided for card payment method")

        elif payment_method == "mtn_momo":
            if not mobile_money_number:
                self.add_error('mobile_money_number', 'MOMO number is required.')
                logger.error("MOMO payment method selected but mobile money number is missing")
            if card_number or card_expiry or card_cvv:
                self.add_error(None, 'Credit card details are not required for MOMO payment.')
                logger.error("Credit card details provided for MOMO payment method")

        return cleaned_data
    


class UpdateBillingInformationForm(forms.ModelForm):
    """
    A form for updating billing information.
    """
    payment_method = forms.ChoiceField(choices=[('', 'Select a payment method')] + BillingInformation.PAYMENT_METHODS, required=True, label='Payment Method')
    card_expiry = forms.CharField(required=False, label='Card Expiry', widget=forms.TextInput(attrs={'placeholder': 'mm/yy'}))

    class Meta:
        model = BillingInformation
        fields = ['payment_method', 'mobile_money_number', 'card_number', 'card_expiry', 'card_cvv']

    def clean_card_expiry(self):
        """
        Validates the credit card expiry date and raises a ValidationError if it's empty or not in the correct format.

        Args:
            self: An instance of UpdateBillingInformationForm.

        Returns:
            card_expiry (str): The validated credit card expiry date.

        Raises:
            ValidationError: If the credit card expiry date is empty or not in the correct format.

        """
        card_expiry = self.cleaned_data.get('card_expiry')
        if card_expiry and not re.match(r'^(0[1-9]|1[0-2])\/\d{2}$', card_expiry):
            logger.error(f"Invalid card expiry date format: {card_expiry}")
            raise forms.ValidationError('Card expiry must be in mm/yy format.')
        return card_expiry
    
    def clean(self):
        """
        Validates the form data and raises a ValidationError if any field fails validation.

        Args:
            self: An instance of UpdateBillingInformationForm.

        Returns:
            cleaned_data (dict): A dictionary containing the validated form data.

        Raises:
            ValidationError: If any field fails validation.

        """
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        mobile_money_number = cleaned_data.get('mobile_money_number')
        card_number = cleaned_data.get('card_number')
        card_expiry = cleaned_data.get('card_expiry')
        card_cvv = cleaned_data.get('card_cvv')

        if payment_method == "card":
            if not card_number:
                self.add_error('card_number', 'Card number is required.')
                logger.error("Card payment method selected but card number is missing")
            if not card_expiry:
                self.add_error('card_expiry', 'Card expiry date is required.')
                logger.error("Card payment method selected but card expiry date is missing")
            if not card_cvv:
                self.add_error('card_cvv', 'Card CVV is required.')
                logger.error("Card payment method selected but card CVV is missing")
            if mobile_money_number:
                self.add_error('mobile_money_number', 'MOMO number is not required for Card payment.')
                logger.error("Mobile money number provided for card payment method")

        elif payment_method == "mtn_momo":
            if not mobile_money_number:
                self.add_error('mobile_money_number', 'MOMO number is required.')
                logger.error("MOMO payment method selected but mobile money number is missing")
            if card_number or card_expiry or card_cvv:
                self.add_error(None, 'Credit card details are not required for MOMO payment.')
                logger.error("Credit card details provided for MOMO payment method")

        return cleaned_data
    