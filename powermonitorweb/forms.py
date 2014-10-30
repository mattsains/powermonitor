from django import forms
from django.contrib.auth.models import User
from powermonitorweb.models import SocialMediaAccount, Report, UserReports, Alert, UserAlerts
from powermonitorweb import widgets


class UserForm(forms.ModelForm):
    """
    Get the user's information.
    """
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        """
        Define the fields that will be shown on the form
        """
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password', 'confirm_password')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        # Remove the annoying help text from add user form
        self.fields['username'].help_text = None

    def clean(self):
        super(UserForm, self).clean()
        if self.cleaned_data.get('password') != self.cleaned_data.get('confirm_password'):
            raise forms.ValidationError("Passwords must match.")
        return self.cleaned_data


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class HouseholdSetupUserForm(forms.ModelForm):
    """
    Get the homeowner's details
    """
    class Meta:
        """
        Define the fields that will be shown on the form
        """
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password', 'confirm_password')

    password = forms.CharField(widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean(self):
        if self.cleaned_data.get('password') != self.cleaned_data.get('confirm_password'):
            raise forms.ValidationError("Passwords must match.")
        return self.cleaned_data


class SocialMediaAccountForm(forms.ModelForm):
    class Meta:
        model = SocialMediaAccount
        fields = (
            'post_daily',  # automatically post daily reports?
            'post_weekly',  # automatically post weekly reports?
            'post_monthly',  # automatically post monthly reports?
            'post_yearly',  # automatically post yearly reports?
            'is_enabled'  # is the account enabled or not?
        )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(SocialMediaAccountForm, self).__init__(*args, **kwargs)

        self.fields['post_daily'] = forms.ChoiceField(widget=forms.CheckboxInput())
        self.fields['post_weekly'] = forms.ChoiceField(widget=forms.CheckboxInput())
        self.fields['post_monthly'] = forms.ChoiceField(widget=forms.CheckboxInput())
        self.fields['post_yearly'] = forms.ChoiceField(widget=forms.CheckboxInput())
        self.fields['is_enabled'] = forms.ChoiceField(widget=forms.RadioSelect,
                                                      choices=[('0', 'disabled'), ('1', 'enabled')])


#The following 2 forms are displayed together on the manage reports page
class ReportTypeForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ('report_type',)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(ReportTypeForm, self).__init__(*args, **kwargs)

        enabled_choices = []
        choices = []
        remainder = []

        # create a list of IDs of all enabled reports
        for a in Report.objects.all().select_related("users").filter(users=user.id):
            enabled_choices.append(a.id)

        for a in Report.objects.all():
            if a.id in enabled_choices:
                choices.append((a.id, a.report_type))
            else:
                remainder.append((a.id, a.report_type))

        choices = choices + remainder

        self.fields['report_type'] = forms.ChoiceField(
            widget=widgets.EnabledSelect(enabled_choices, attrs={'size': '15', 'required': 'true', 'class':'form-control'}),
            choices=choices, label='Reports')


class ReportDetailsForm(forms.ModelForm):
    class Meta:

        model = UserReports
        fields = (
            'occurrence_type',
            'datetime',
            'report_daily',
            'report_weekly',
            'report_monthly')

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')   # Not sure what you wanted to do with this. I added this to fix the errors I was getting
        super(ReportDetailsForm, self).__init__(*args, **kwargs)

        # generated fields work for everything else but this needs to be custom
        self.fields['occurrence_type'] = forms.ChoiceField(widget=forms.Select,
                                                           choices=[('1', 'recurring'), ('0', 'once-off')])
        self.fields['datetime'].label = "Date and time"


#The following 2 forms are displayed together on the manage reports page
class AlertTypeForm(forms.ModelForm):
    class Meta:
        model = Alert
        fields = ('alert_description',)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(AlertTypeForm, self).__init__(*args, **kwargs)

        enabled_choices = []
        choices = []
        remainder = []

        # create a list of IDs of all enabled reports
        for a in Alert.objects.all().select_related("users").filter(users=user.id):
            enabled_choices.append(a.id)

        for a in Alert.objects.all():
            if a.id in enabled_choices:
                choices.append((a.id, a.alert_name))
            else:
                remainder.append((a.id, a.alert_name))

        choices = choices + remainder

        self.fields['alert_type'] = forms.ChoiceField(
            widget=widgets.EnabledSelect(enabled_choices, attrs={'size': '15', 'required': 'true','class':'form-control'}),
            choices=choices, label='Alerts')


class AlertDetailsForm(forms.ModelForm):
    class Meta:

        model = UserAlerts
        fields = (
            'user_id',
            'alert_id',)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')   # Not sure what you wanted to do with this. I added this to fix the errors I was getting
        super(AlertDetailsForm, self).__init__(*args, **kwargs)

class UserListForm(forms.Form):
    class Meta:
        fields = ('users',)

    def __init__(self, *args, **kwargs):
        users = kwargs.pop('user_list')
        super(UserListForm, self).__init__(*args, **kwargs)
        self.fields['users'] = forms.ChoiceField(widget=forms.Select(attrs={'size': '11', 'required': 'true','class':'form-control'}),
                                                 choices=users)


class ManageUsersForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'required': True}), max_length=255)
    first_name = forms.CharField(widget=forms.TextInput(attrs={'required': True}), max_length=255)
    last_name = forms.CharField(widget=forms.TextInput(attrs={'required': True}), max_length=255)
    email = forms.EmailField(widget=forms.EmailInput(attrs={'required': True}))

    class Meta:
        fields = (
            'username', 'first_name', 'last_name', 'email', 'password'
        )

period_list = [
    ('1hour', 'Last Hour'),
    ('12hour', 'Last 12 Hours'),
    ('day', 'Last Day'),
    ('week', 'Last Week'),
    ('1month', 'Last Month'),
    ('6month', 'Last 6 Months'),
    ('year', 'Last Year'),
    ('predict', '1 Hour Prediction')]


class SelectGraphPeriodForm(forms.Form):
    period = forms.ChoiceField(widget=forms.Select, choices=period_list)
