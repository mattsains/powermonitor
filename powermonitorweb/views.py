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

from powermonitorweb.forms import UserForm, SelectGraphPeriodForm
from powermonitorweb.forms import HouseholdSetupUserForm, SocialMediaAccountForm, ReportTypeForm, ReportDetailsForm, \
    ManageUsersForm, UserListForm, ProfileForm
from powermonitorweb.models import Report, ElectricityType, User, UserReports
# requirements for graphing
from DataAnalysis.Forecasting import PowerForecasting as pf
from DataAnalysis.Plotting import Plotter as plt
from DataAnalysis.DataFrameCollector import DataFrameCollector as dfc
from DataAnalysis.PowerAlertScraper import PowerAlertScraper as PAS
from datetime import datetime
from dateutil.relativedelta import relativedelta
import os

@login_required()
def index(request):
    context = RequestContext(request)
    return render_to_response('powermonitorweb/index.html', {}, context)
    #return HttpResponseRedirect('/powermonitorweb/graphs/')  # start at the graphs page


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
        norow = True
    else:
        setup = bool(issetup[0])
    
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

            if norow:
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
    user_reports = UserReports.objects.all().filter(user_id=user.id)
    user_report_details = None

    if request.is_ajax():
        datadict = request.POST
        if datadict.get('identifier') == 'id_report_type_change':
            #User has clicked on a different user, so update the form
            try:
                myreport = user_reports.filter(report_id=datadict.get('report_type'))
            except Exception:
                myreport = None

            JSONdata = serializers.serialize('json', myreport, fields=('occurrence_type', 'datetime', 'report_daily',
                                                                       'report_weekly', 'report_monthly'))
            print (JSONdata)
            print("end")
        else:
            JSONdata = '[{}]'

        return HttpResponse(JSONdata.replace('[', '').replace(']', ''))  # clean and send data
    elif request.method == 'POST':
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
    users = User.objects.filter(is_superuser='0')  # the homeowner can manage their profile the same as normal users
    user_list = [(u.id, u.username) for u in users]

    if request.is_ajax():
        # Create JSON object to pass back to the page so that fields can be populated
        datadict = request.POST
        # print(datadict.get('identifier'))
        JSONdata = None
        saved = None
        if datadict.get('identifier') == 'update_user_click':
            save_user = User.objects.get(id=datadict.get('users'))
            # user has clicked "update"
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
        elif datadict.get('identifier') == 'reset_password_click':
            # User has clicked "Reset Password"
            form = PasswordResetForm({'email': str(datadict.get('email'))})
            try:
                if form.is_valid():
                    saved = form.save(email_template_name='powermonitorweb/reset_password_email.html', request=request)
            except Exception as e:
                saved = 'false'
            if saved is None:
                saved = 'true'
            JSONdata = '{"email_sent": %s}' % saved
        elif datadict.get('identifier') == 'id_users_change':
            #User has clicked on a different user, so update the form
            JSONdata = serializers.serialize('json', User.objects.filter(id=datadict.get('users')),
                                             fields=('username', 'first_name', 'last_name', 'email'))
        elif datadict.get('identifier') == 'delete_user_click':
            # Delete the selected user
            user = User.objects.get(id=datadict.get('users'))
            if user:
                user.delete()
                JSONdata = '{"deleted": true}'
            else:
                JSONdata = '{"deleted": false}'
        else:
            JSONdata = "[{}]"   # Give it an empty dictionary
        return HttpResponse(JSONdata.replace('[', '').replace(']', ''))  # clean and send data

    elif request.method == 'POST':
        # otherwise we got a post request, so we must handle it
        # Save the add user data
        add_user_form = UserForm(data=request.POST)
        if add_user_form.is_valid():
            add_user_form.save()
            user_added = True
        else:
            print add_user_form.errors
            user_added = False
        # These two are handled with Ajax, so ignore them
        manage_users_form = ManageUsersForm()
        users = User.objects.filter(is_superuser='0')   # refresh the user list for the new user
        user_list = [(u.id, u.username) for u in users]
        user_list_form = UserListForm(user_list=user_list)
    else:
        manage_users_form = ManageUsersForm()
        user_list_form = UserListForm(user_list=user_list)
        add_user_form = UserForm()
        user_added = False

    return render_to_response(
        'powermonitorweb/manage_users.html',
        {
            'manage_users_form': manage_users_form,
            'user_list_form': user_list_form,
            'add_user_form': add_user_form,
            'user_added': user_added
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


@login_required()
def profile(request):
    """
    Manage profile page for users
    """
    context = RequestContext(request)
    user = request.user
    if request.method == 'POST':
        profile_form = ProfileForm(data=request.POST, instance=request.user)
        if profile_form.is_valid():
            if request.POST['first_name'] and user.first_name != request.POST['first_name']:
                user.first_name = request.POST['first_name']
            if request.POST['last_name'] and user.last_name != request.POST['last_name']:
                user.last_name = request.POST['last_name']
            if request.POST['email'] and user.email != request.POST['email']:
                user.email = request.POST['email']
            user.save()
        else:
            print profile_form.errors
    else:
        profile_form = ProfileForm(instance=request.user)
    return render_to_response(
        'powermonitorweb/profile.html',
        {'profile_form': profile_form},
        context
        )


# THIS METHOD IS NOT A VIEW!!!
def generate_usage_graph(period_type, length, file_path):
        graph_name = 'null'
        if period_type == 'hour':
            delta = relativedelta(hours=length)
        elif period_type == 'day':
            delta = relativedelta(days=length)
        elif period_type == 'week':
            delta = relativedelta(weeks=length)
        elif period_type == 'month':
            delta = relativedelta(months=length)
        else:
            delta = relativedelta(years=length)
        frame = dfc().collect_period(period_type=period_type,
                                     period_start=str(datetime.now().replace(microsecond=0) - delta),
                                     period_length=length)
        if frame is not None:
            graph_name = 'last_%d%s.svg' % (length, period_type)
            plot_title = 'Last %d %s' % (length, period_type.capitalize())
            plt().plot_single_frame(data_frame=frame, title=plot_title, y_label='Usage (kW)',
                                    x_label='Time', file_name=file_path + graph_name)
        return graph_name


# THIS METHOD IS NOT A VIEW!!!
def generate_prediction_graph(file_path):
    graph_name = 'null'
    try:
        # For now pass a 12hr frame to be on the safe side. The forecasting cuts quite a bit off
        pre_predction_frame = dfc().collect_period(period_type='hour',
                                                   period_start=str(datetime.now().replace(microsecond=0) -
                                                                    relativedelta(hours=12)),
                                                   period_length=12)
        if pre_predction_frame is not None:
            prediction_frame = pf().predict_usage(data_frame=pre_predction_frame, smooth=True)
            plt().plot_single_frame(data_frame=prediction_frame, title='Predicted Usage', y_label='Usage (kW)',
                                    x_label='Time', file_name=file_path + graph_name, prediction=True)
            graph_name = 'prediction_graph.svg'
    except:
        pass
    return graph_name

# THIS METHOD IS NOT A VIEW!!!
scraper = PAS()

def get_current_statistics():
    current_usage = None
    average_usage = None
    savings = None

    try:
        frame = dfc().collect_period(period_type='hour', period_start=str(
            datetime.now().replace(microsecond=0) - relativedelta(hours=1)), period_length=1)
        current_usage = frame.tail(1).iloc[0]['reading']
        average_usage = frame.mean(axis=0)['reading']
    except:
        pass
    stats = scraper.get_stats()
    eskom_colour = stats['eskom_colour']
    eskom_usage = stats['eskom_usage']

    if current_usage is None:
        current_usage = float(0)
    if average_usage is None:
        average_usage = float(0)

    return {'current_usage': '%.2f' % current_usage, 'average_usage': '%.2f' % average_usage, 'savings': savings,
            'eskom_status': '%s_%s' % (eskom_colour, eskom_usage)}


@login_required()
def graphs(request):
    """
    Generates a new graph when a user requests it. I think we should stick away from live graphs for now to keep some of
    the strain off the CPU. We don't know yet how the whole system will perform when everything is running.
    :param request:
    :return:
    """
    context = RequestContext(request)
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'powermonitorweb\\static\\powermonitorweb\\'
                                                                        'images\\graphs\\')
    graph_name = 'null'

    if request.is_ajax():   # The user has selected a different graph
        datadict = request.POST
        # generate a new graph based on the user's selection
        if datadict.get('period') == '1hour':
            graph_name = generate_usage_graph(period_type='hour', length=1, file_path=file_path)
        elif datadict.get('period') == '12hour':
            graph_name = generate_usage_graph(period_type='hour', length=12, file_path=file_path)
        elif datadict.get('period') == 'day':
            graph_name = generate_usage_graph(period_type='day', length=1, file_path=file_path)
        elif datadict.get('period') == 'week':
            graph_name = generate_usage_graph(period_type='week', length=1, file_path=file_path)
        elif datadict.get('period') == '1month':
            graph_name = generate_usage_graph(period_type='month', length=1, file_path=file_path)
        elif datadict.get('period') == '6month':
            graph_name = generate_usage_graph(period_type='month', length=6, file_path=file_path)
        elif datadict.get('period') == 'year':
            graph_name = generate_usage_graph(period_type='year', length=1, file_path=file_path)
        elif datadict.get('period') == 'predict':
            # Generating a prediction graph works a little differently
            graph_name = generate_prediction_graph(file_path=file_path)
        if graph_name != 'null':
            # A graph was produced!
            # It seemed easier to generate the html tag here, then just use JS to plonk it in the div
            graph_html = "<img src='/static/powermonitorweb/images/graphs/%s' />" % graph_name
        else:
            graph_html = "<strong>No graph found. There may be insufficient data to generate a graph.<br />" \
                         "Try selecting another period.</strong>" \
                         "<p>If a power outage has occurred, you may need to wait 12hours before predictions can be " \
                         "calculated</p>"
        current_stats = get_current_statistics()
        # return the name of the new graph to display
        JSONdata = '{"graph": "%s", "current_usage": "%s", "average_usage": "%s", "eskom_status": "%s", ' \
                   '"savings": "%s"}' % (graph_html, current_stats['current_usage'], current_stats['average_usage'],
                    current_stats['eskom_status'], current_stats['savings'])
        print JSONdata
        return HttpResponse(JSONdata)
    else:
        # otherwise the page was loaded, so show a default graph. currently defaults to 12hr graph
        graph_period_form = SelectGraphPeriodForm(initial={'period': '12hour'})
        graph_name = generate_usage_graph(period_type='hour', length=12, file_path=file_path)
        current_stats = get_current_statistics()
        status_image = '%s.svg' % current_stats['eskom_status']
    return render_to_response(
        'powermonitorweb/graphs.html',
        {
            'graph': graph_name,
            'graph_period_form': graph_period_form,
            'current_usage': current_stats['current_usage'],
            'average_usage': current_stats['average_usage'],
            'eskom_status': status_image,
            'savings': current_stats['savings']
        },
        context
    )