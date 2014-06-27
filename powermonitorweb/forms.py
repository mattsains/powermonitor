from django import forms
from django.contrib.auth.models import User
from powermonitorweb.models import SocialMediaAccount


class UserForm(forms.ModelForm):
    """
    Get the user's information.
    """
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        """
        Define the fields that will be shown on the form
        """
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password')


class HouseholdSetupUserForm(forms.ModelForm):
    """
    Get the homeowner's details
    """
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        """
        Define the fields that will be shown on the form
        """
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password')