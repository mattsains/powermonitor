from django import forms
from django.contrib.auth.models import User
from powermonitorweb.models import Food, ElectricityType

class UserForm(forms.ModelForm):
    '''
    Get the user's information.
    '''
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        '''
        Define the fields that will be shown on the form
        '''
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password')

class HouseholdSetupUserForm(forms.ModelForm):
    '''
    Get the homeowner's details
    '''
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        '''
        Define the fields that will be shown on the form
        '''
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password')

class HouseholdSetupFoodsForm(forms.ModelForm):
    '''
    Get the foods that the household generally keeps
    '''
    class Meta:
        '''
        Define the fields that will be shown on this form
        '''
        model = Food
        food_description = forms.ChoiceField(widget=forms.SelectMultiple, choices=list(Food.objects.all()))

class HouseholdElectricityForm(forms.ModelForm):
    '''
    Get the household electricity type
    '''
    class Meta:
        model = ElectricityType
        #electricity_type = forms.ChoiceField(widget=forms.RadioSelect, choices=('Prepaid', 'Topup',))