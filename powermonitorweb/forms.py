from django import forms
from django.contrib.auth.models import User
from powermonitorweb.models import SocialMediaAccount, Report, UserReports


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
            raise forms.ValidationError("Email addresses must match.")
        return self.cleaned_data


class SocialMediaAccountForm(forms.ModelForm):
    class Meta:
        model = SocialMediaAccount
        fields = (
            'account_type',  # a select list of accounts for the user
            'account_username',  # the username for the social media account
            'account_token', # the authentication token given by the social media service
            'post_daily',  # automatically post daily reports?
            'post_weekly',  # automatically post weekly reports?
            'post_monthly',  # automatically post monthly reports?
            'post_yearly',  # automatically post yearly reports?
            'is_enabled'  # is the account enabled or not?
        )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(SocialMediaAccountForm, self).__init__(*args, **kwargs)
        choice_list = [
            (a.id, a.account_type)
            for a in SocialMediaAccount.objects.all().select_related('users').filter(users=user.id)]

        self.fields['account_type'] = forms.ChoiceField(
            widget=forms.Select(attrs={'size': '5', 'required': 'true'}), choices=choice_list)
        self.fields['account_username'] = forms.CharField(widget=forms.TextInput)
        self.fields['account_token'] = forms.CharField(widget=forms.TextInput)
        self.fields['post_daily'] = forms.ChoiceField(widget=forms.CheckboxInput())
        self.fields['post_weekly'] = forms.ChoiceField(widget=forms.CheckboxInput())
        self.fields['post_monthly'] = forms.ChoiceField(widget=forms.CheckboxInput())
        self.fields['post_yearly'] = forms.ChoiceField(widget=forms.CheckboxInput())
        self.fields['is_enabled'] = forms.ChoiceField(widget=forms.RadioSelect,
                                                      choices=[('0', 'disabled'), ('1', 'enabled')])


class ReportTypeForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ('report_type',)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(ReportTypeForm, self).__init__(*args, **kwargs)

        choice_list = [
            (a.id, a.report_type)
            for a in Report.objects.all().select_related('users').filter(users=user.id)]
        print choice_list
        self.fields['report_type'] = forms.ChoiceField(
            widget=forms.Select(attrs={'size': '5', 'required': 'true'}), choices=choice_list)

class ReportDetailsForm(forms.ModelForm):
    class Meta:
        model = UserReports
        fields = (
            'user_reports_list',
            'occurrence_type',
            'datetime',
            'report_daily',
            'report_weekly',
            'report_monthly')

    user_reports_list = forms.ChoiceField(
        widget=forms.Select(attrs={'size': '5', 'required': 'true'}))

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(ReportDetailsForm, self).__init__(*args, **kwargs)
        self.fields['user_reports_list'] = forms.ChoiceField(
            widget=forms.Select(attrs={'size': '5', 'required': 'true'}))
        self.fields['occurrence_type'] = forms.ChoiceField(widget=forms.Select,
                                                           choices=[('1', 'Recurring'), ('0','Once-Off')])
        self.fields['datetime'] = forms.SplitDateTimeField(widget=forms.SplitDateTimeWidget())
        self.fields['report_daily'] = forms.ChoiceField(widget=forms.CheckboxInput())
        self.fields['report_weekly'] = forms.ChoiceField(widget=forms.CheckboxInput())
        self.fields['report_monthly'] = forms.ChoiceField(widget=forms.CheckboxInput())
