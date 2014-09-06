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
    ManageUsersForm, UserListForm, ProfileForm, UserAlerts, AlertTypeForm, AlertDetailsForm
from powermonitorweb.models import Report, ElectricityType, User, UserReports, Alert, UserAlerts
from powermonitorweb.utils import createmessage
# requirements for graphing
from DataAnalysis.Stats import PowerForecasting as forecast
from DataAnalysis.Plotting import Plotter as plt
from DataAnalysis.DataFrameCollector import DataFrameCollector as dfc
from DataAnalysis.PowerAlertScraper import PowerAlertScraper as PAS
from DataAnalysis.Resampling import Resampling
from datetime import datetime
from dateutil.relativedelta import relativedelta
import os

@login_required()
def index(request):
    context = RequestContext(request)
    # return render_to_response('powermonitorweb/index.html', {}, context)
    return HttpResponseRedirect('/powermonitorweb/graphs/')  # start at the graphs page


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
def manage_alerts(request):
    context = RequestContext(request)
    posted = False

    user = request.user
    user_alerts = UserAlerts.objects.all().filter(user_id=user.id)
    alerts = Alert.objects.all();
    user_alert_details = None
    if request.is_ajax():
        datadict = request.POST

        if datadict.get('identifier') == 'id_alert_type_change':

            myalert = alerts.filter(id=datadict.get('alert_type'))
            print myalert
            if len(myalert) == 1:
                JSONdata = serializers.serialize('json', myalert, fields=('alert_description',))
            else:
                # send blank fields to override values as a reset mechanism
                JSONdata = '{ "fields":{"alert_description" : ""}}'
        elif datadict.get('identifier') == 'enable_alert_click':
            rec_alert_id = Alert.objects.get(id=int(datadict.get('alert_type')))
            alert_details_model = UserAlerts(user_id=user, alert_id= rec_alert_id);
            alert_details_model.save()
            JSONdata = createmessage(True, 'Alert Changes Saved', 'Your alert has been activated')
        elif datadict.get('identifier') == 'disable_alert_click':
            alert_to_delete = user_alerts.filter(alert_id=Alert.objects.get(id=datadict.get('alert_type')))
            alert_to_delete.delete()
            JSONdata = createmessage(True, 'Alert Disabled', 'The alert was disabled')
        else:
            JSONdata = '[{}]'

        return HttpResponse(JSONdata.replace('[', '').replace(']', ''))  # clean and send data
    elif request.method == 'POST':
        alert_type_form = AlertTypeForm(data=request.POST, user=user)
        alert_details_form = AlertDetailsForm(data=request.POST, user=user)
    else:
        alert_type_form = AlertTypeForm(user=user)
        alert_details_form = AlertDetailsForm(user=user)

    return render_to_response(
        'powermonitorweb/manage_alerts.html',
        {
            'posted': posted, 'alert_type_form': alert_type_form, 'alert_details_form': alert_details_form,
            'user_reports': user_alerts, 'user_report_details': user_alert_details
        },
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
            myreport = user_reports.filter(report_id=datadict.get('report_type'))
            if len(myreport) == 1:
                JSONdata = serializers.serialize('json', myreport, fields=('occurrence_type', 'datetime', 'report_daily',
                                                                           'report_weekly', 'report_monthly'))
                JSONdata = JSONdata.replace('-', '/').replace('T', ' ')[:-8] + '"}}'
            else:
                # send blank fields to override values as a reset mechanism
                JSONdata = '{ "fields":{"occurrence_type" : "", "datetime" : "", "report_daily": "",' \
                           '"report_weekly": "", "report_monthly": ""}}'
        elif datadict.get('identifier') == 'enable_report_click':
            report_type = Report.objects.get(id=int(datadict.get('report_type')))
            occurrence_type = int(datadict.get('occurrence_type'))
            datetime = str(datadict.get('datetime')).replace('/', '-')
            report_daily = not (datadict.get('report_daily') is None)
            report_weekly = not (datadict.get('report_weekly') is None)
            report_monthly = not (datadict.get('report_monthly')is None)

            report_details_model = UserReports(user_id=user,
                                               report_id=report_type,
                                               occurrence_type=occurrence_type,
                                               datetime=datetime,
                                               report_daily=report_daily,
                                               report_weekly=report_weekly,
                                               report_monthly=report_monthly)

            report_details_model.save()

            if (True): #TODO: validation should happen
                JSONdata = createmessage(True, 'Report Enabled', 'Successfully enabled [report name]')
            else:
                JSONdata = createmessage(False, 'Error', 'The report could not be enabled')

        elif datadict.get('identifier') == 'disable_report_click':
            report_to_delete = user_reports.filter(report_id=Report.objects.get(id=datadict.get('report_type')))
            report_to_delete.delete()
            JSONdata = createmessage(True, 'Report Disabled', 'The report was disabled')

        elif datadict.get('identifier') == 'save_report_click':
            print("trying to save")

            # update changed fields.
            report_type = Report.objects.get(id=int(datadict.get('report_type')))
            occurrence_type = int(datadict.get('occurrence_type'))
            datetime = str(datadict.get('datetime')).replace('/', '-')
            report_daily = not (datadict.get('report_daily') is None)
            report_weekly = not (datadict.get('report_weekly') is None)
            report_monthly = not (datadict.get('report_monthly')is None)

            report_to_change = user_reports.get(report_id=report_type)

            if report_to_change.datetime != datetime:
                report_to_change.datetime = datetime
            if report_to_change.occurrence_type != occurrence_type:
                print occurrence_type
                report_to_change.occurrence_type = occurrence_type
            if report_to_change.report_daily != report_daily:
                report_to_change.report_daily = report_daily
            if report_to_change.report_weekly != report_weekly:
                report_to_change.report_weekly = report_weekly
            if report_to_change.report_monthly != report_monthly:
                report_to_change.report_monthly = report_monthly

            # save to db
            try:
                report_to_change.save()
            except:
                print("lol")
            JSONdata = createmessage(True, 'Report Changes Saved', 'All changes to this report have been saved')
        else:
            JSONdata = '[{}]'

        return HttpResponse(JSONdata.replace('[', '').replace(']', ''))  # clean and send data
    elif request.method == 'POST':
        report_type_form = ReportTypeForm(data=request.POST, user=user)
        report_details_form = ReportDetailsForm(data=request.POST, user=user)
    else:
        report_type_form = ReportTypeForm(user=user)
        report_details_form = ReportDetailsForm(user=user)

    return render_to_response(
        'powermonitorweb/manage_reports.html',
        {
            'posted': posted, 'report_type_form': report_type_form, 'report_details_form': report_details_form,
            'user_reports': user_reports, 'user_report_details': user_report_details
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
            password_reset_form = PasswordResetForm({'email': str(datadict.get('email'))})
            try:
                if password_reset_form.is_valid():
                    saved = password_reset_form.save(email_template_name='powermonitorweb/reset_password_email.html',
                                                     request=request)
            except:
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
            try:  # try deleting the file
                os.remove(file_path + graph_name)
            except:
                pass  # don't care if it can't find the file. a new one is being created anyway
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
            graph_name = 'prediction_graph.svg'
            try:    # try delete the file. This should hopefully prevent any issues
                os.remove(file_path + graph_name)
            except:
                pass  # if it doesn't exist it can't be deleted
            plt().plot_single_frame(data_frame=prediction_frame, title='Predicted Usage', y_label='Usage (W)',
                                    x_label='Time', file_name=file_path + graph_name, prediction=True)
    except:
        pass
    return graph_name

scraper = PAS()


# THIS METHOD IS NOT A VIEW!!!
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
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'powermonitorweb', 'static', 'powermonitorweb',
                             'images', 'graphs', '')  # new unix friendly flavour! Forgot the trailing slash...
    graph_name = 'null'
    frame = None
    if request.is_ajax():   # The user has selected a different graph
        datadict = request.POST
        # generate a new graph based on the user's selection
        if datadict.get('period') == '1hour':
            frame = dfc().collect_period(period_type='hour', period_start=str(
                datetime.now().replace(microsecond=0) - relativedelta(hours=1)), period_length=1)
        elif datadict.get('period') == '12hour':
            frame = dfc().collect_period(period_type='hour', period_start=str(
                datetime.now().replace(microsecond=0) - relativedelta(hours=12)), period_length=12)
        elif datadict.get('period') == 'day':
            frame = dfc().collect_period(period_type='day', period_start=str(
                datetime.now().replace(microsecond=0) - relativedelta(days=1)), period_length=1)
        elif datadict.get('period') == 'week':
            frame = dfc().collect_period(period_type='week', period_start=str(
                datetime.now().replace(microsecond=0) - relativedelta(weeks=1)), period_length=1)
        elif datadict.get('period') == '1month':
            frame = dfc().collect_period(period_type='month', period_start=str(
                datetime.now().replace(microsecond=0) - relativedelta(months=1)), period_length=1)
        elif datadict.get('period') == '6month':
            frame = dfc().collect_period(period_type='month', period_start=str(
                datetime.now().replace(microsecond=0) - relativedelta(months=6)), period_length=6)
        elif datadict.get('period') == 'year':
            frame = dfc().collect_period(period_type='year', period_start=str(
                datetime.now().replace(microsecond=0) - relativedelta(years=1)), period_length=1)
        
        elif datadict.get('period') == 'predict':
            # Generating a prediction graph works a little differently
            #TODO: do this
            pass

        points = None
        try:
            points = Resampling().buildArrayTimeReading(frame)
        except:
            pass  # Will sending empty points to the graph give an error?
            
        json_graph="["+",".join(map(lambda x: "["+str(Resampling().timestamp_to_milliseconds(x[0]))+","+str(x[1])+"]", points))+"]"
        
        current_stats = get_current_statistics()
        # return the name of the new graph to display
        JSONdata = '{"graph": '+json_graph+', "current_usage": "%s", "average_usage": "%s", "eskom_status": "%s", ' \
                   '"savings": "%s"}' % (current_stats['current_usage'], current_stats['average_usage'],
                    current_stats['eskom_status'], current_stats['savings'])
        return HttpResponse(JSONdata)
    else:
        # otherwise the page was loaded, so show a default graph. currently defaults to 12hr graph
        graph_period_form = SelectGraphPeriodForm(initial={'period': '12hour'})
        # This doesn't need to be generated any more
        # graph_name = generate_usage_graph(period_type='hour', length=12, file_path=file_path)
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