from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db import connection
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import password_change, password_reset, password_reset_confirm, password_reset_complete
from django.core import serializers
from django.core.urlresolvers import reverse

from powermonitorweb.forms import UserForm
from powermonitorweb.forms import HouseholdSetupUserForm, SocialMediaAccountForm, ReportTypeForm, ReportDetailsForm, \
    ManageUsersForm, UserListForm
from powermonitorweb.models import Report, ElectricityType, User

@login_required()
def index(request):
    context = RequestContext(request)
    return render_to_response('powermonitorweb/index.html', {}, context)


def setup_household(request):
    """
    Setup up the household profile
    REQUIRED:   The database table powermonitorweb_configuratin must have data. This should be set up when the system
                is deployed and should not require intervention from the user.
    """
    context = RequestContext(request)
    electricity_type = ElectricityType.objects.all()
    cursor = connection.cursor()
    cursor.execute("SELECT value FROM powermonitorweb_configuration WHERE field='is_setup'")
    norow = False
    issetup = cursor.fetchone()
    if issetup is None:
        setup = False
    else:
        setup = bool(issetup[0])
        norow = True
    
    if setup:
        return HttpResponseRedirect('/powermonitorweb/')

    if request.method == 'POST':
        setup_homeowner_form = HouseholdSetupUserForm(data=request.POST)

        elec = request.POST['electricity_type']

        if setup_homeowner_form.is_valid():
            homeowner = setup_homeowner_form.save()
            homeowner.set_password(homeowner.password)
            homeowner.is_superuser = True
            homeowner.save()

            if not norow:
                cursor.execute("INSERT INTO powermonitorweb_configuration(field, value) VALUES ('is_setup',1)")
            else:
                cursor.execute("UPDATE powermonitorweb_configuration SET value=1 WHERE field='is_setup'")
            setup = True
        else:
            print setup_homeowner_form.errors
    else:
        setup_homeowner_form = HouseholdSetupUserForm()

    return render_to_response(
        'powermonitorweb/setup_household.html',
        {'setup_homeowner_form': setup_homeowner_form,
         'electricity_type': electricity_type,
         'setup': setup},
        context)


@login_required()
def add_user(request):
    """
    Add User view.
    Add a new user to the system. Only the homeowner is able to access this.
    """
    context = RequestContext(request)
    if not request.user.is_authenticated() or not request.user.is_superuser:
        return render_to_response('powermonitorweb/not_admin.html')
    registered = False

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)

        if user_form.is_valid():
            user = user_form.save()

            user.set_password(user.password)
            user.save()

            registered = True
        else:
            print user_form.errors
    else:
        user_form = UserForm()

    return render_to_response(
        'powermonitorweb/add_user.html',
        {'user_form': user_form, 'registered': registered},
        context
    )


def user_login(request):
    context = RequestContext(request)

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:  # added this in case we want to use this functionality
                login(request, user)
                return HttpResponseRedirect('/powermonitorweb/')
            else:
                return HttpResponse('This account is disabled')
        else:
            return render_to_response(
                'powermonitorweb/invalid_login.html',
                {'username': username},
                context
            )
    else:
        return render_to_response('powermonitorweb/login.html', {}, context)


@login_required()   # You can only logout if you're already logged in...obviously
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/powermonitorweb/')


from powermonitorweb.models import SocialMediaAccount
@login_required()
def post_to_socialmedia(request):
    """
    Display options for the user to select which social media to post to.
    """
    # TODO: This needs to be complete once we are actually able to post to social media sites
    context = RequestContext(request)

    user = request.user
    user_accounts = \
        SocialMediaAccount.objects.all().select_related('users').filter(users=user.id)

    failed = False
    posted = False

    if request.method == 'POST':
        account = request.POST.get('account_select')
        posts = request.POST.getlist('posts')
        period = request.POST.get('period_select')

        if any(posts):
            '''If any of the checkboxes are checked, then we can do something.'''
            if 'current_usage' in posts:
                # TODO: Post current usage to selected social media
                pass
            if 'average_usage' in posts:
                # TODO: Post average usage to selected social media
                pass
            if 'savings' in posts:
                # TODO: Post savings to selected social media
                pass
            if 'graph' in posts:
                # TODO: Post graph of usage to selected social media
                pass
            posted = True
        else:
            '''Nothing was posted, so we must tell the user to select a checkbox'''
            failed = True

    return render_to_response(
        'powermonitorweb/post_to_socialmedia.html',
        {'failed': failed, 'user_accounts': user_accounts, 'posted': posted},
        context
    )


@login_required()
def manage_reports(request):
    context = RequestContext(request)
    posted = False

    user = request.user
    user_reports = Report.objects.all().select_related('users').filter(users=user.id)
    user_report_details = None

    if request.method == 'POST':
        report_type_form = ReportTypeForm(data=request.POST, user=request.user)
        report_details_form = ReportDetailsForm(data=request.POST, user=request.user)
    else:
        report_type_form = ReportTypeForm(user=request.user)
        report_details_form = ReportDetailsForm(user=request.user)

    return render_to_response(
        'powermonitorweb/manage_reports.html',
        {
            'posted': posted, 'report_type_form': report_type_form, 'report_details_form': report_details_form,
            'user_reports': user_reports, 'user_report_details': user_report_details
        },
        context
    )


@login_required()
def manage_accounts(request):
    """
    Manage social media accounts
    """
    context = RequestContext(request)

    user = request.user
    user_accounts = SocialMediaAccount.objects.all().select_related('users').filter(users=user.id)

    if request.method == 'POST':
        social_media_account_form = SocialMediaAccountForm(data=request.POST, user=request.user)
    else:
        social_media_account_form = SocialMediaAccountForm(user=request.user, initial={'account_type': '1'})

    return render_to_response(
        'powermonitorweb/manage_accounts.html',
        {
            'social_media_account_form': social_media_account_form,
            'user_accounts': user_accounts
        },
        context
    )


@login_required()
@user_passes_test(lambda u: u.is_superuser)  # Only the homeowner can access this view
def manage_users(request):
    """
    Only the homeowner has permission to manage the user accounts. However, they can't change passwords, only send
    password reset requests.
    """
    context = RequestContext(request)
    users = User.objects.filter(is_superuser='0')
    user_list = [(u.id, u.username) for u in users]

    if request.is_ajax():
        # Create JSON object to pass back to the page so that fields can be populated
        datadict = request.POST
        JSONdata = None
        if datadict.get('users') and datadict.get('username') and datadict.get('first_name') and \
                datadict.get('last_name') and datadict.get('email'):
            save_user = User.objects.filter(id=datadict.get('users'))[0]

            # check each field for a change, and set the new value appropriately
            if save_user.username != datadict.get('username'):
                save_user.username = datadict.get('username')
            if save_user.first_name != datadict.get('first_name'):
                save_user.first_name = datadict.get('first_name')
            if save_user.last_name != datadict.get('last_name'):
                save_user.last_name = datadict.get('last_name')
            if save_user.email != datadict.get('email'):
                save_user.email = datadict.get('email')
            # save the user so it persists to the DB
            save_user.save()
            # send the id and username back so the user list can be updated
            JSONdata = serializers.serialize('json', User.objects.filter(id=save_user.id),
                                             fields=('id', 'username'))
        elif not datadict.get('users') and not datadict.get('username') and not datadict.get('first_name') and not \
                datadict.get('last_name') and datadict.get('email'):
            form = PasswordResetForm({'email': str(datadict.get('email'))})
            try:
                saved = form.save(email_template_name='powermonitorweb/reset_password_email.html', request=request)
            except:
                saved = 'false'
            if saved is None:
                saved = 'true'
            JSONdata = '{"email_sent": %s}' % saved
        elif datadict.get('users'):
            JSONdata = serializers.serialize('json', User.objects.filter(id=datadict.get('users')),
                                             fields=('username', 'first_name', 'last_name', 'email'))
        else:
            JSONdata = "[{}]"
        return HttpResponse(JSONdata.replace('[', '').replace(']', ''))  # clean and send data

    elif request.method == 'POST':
        # otherwise we got a post request, so we must handle it
        manage_users_form = ManageUsersForm(data=request.POST)
        user_list_form = UserListForm(data=request.POST, user_list=user_list)
    else:
        manage_users_form = ManageUsersForm()
        user_list_form = UserListForm(user_list=user_list)

    return render_to_response(
        'powermonitorweb/manage_users.html',
        {
            'manage_users_form': manage_users_form,
            'user_list_form': user_list_form,
        },
        context
    )


@login_required()
def change_password(request):
    return password_change(request=request, template_name='powermonitorweb/change_password.html',
                           post_change_redirect='/powermonitorweb/')


def reset_password_confirm(request, uidb64=None, token=None):
    return password_reset_confirm(request, template_name='powermonitorweb/reset_password_confirm.html', uidb64=uidb64,
                                  token=token, post_reset_redirect=reverse('powermonitorweb:reset_password_complete'))


def reset_password(request):
    return password_reset(request, template_name='powermonitorweb/reset_password.html',
                          email_template_name='powermonitorweb/reset_password_email.html',
                          subject_template_name='powermonitorweb/reset_subject.txt',
                          post_reset_redirect=reverse('powermonitorweb:login'))


def reset_password_complete(request):
    return password_reset_complete(request, template_name='powermonitorweb/reset_password_complete.html')