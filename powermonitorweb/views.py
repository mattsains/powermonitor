from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db import connection
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test

from powermonitorweb.forms import UserForm
from powermonitorweb.forms import HouseholdSetupUserForm
from powermonitorweb.models import Food, ElectricityType


def index(request):
    context = RequestContext(request)
    return render_to_response('powermonitorweb/index.html', {}, context)


def setup_household(request):
    """
    Setup up the household profile
    REQUIRED:   The database table powermonitorweb_issetup must have data. This should be set up when the system
                is deployed and should not require intervention from the user.
    """
    context = RequestContext(request)
    food_list = Food.objects.all()
    electricity_type = ElectricityType.objects.all()
    cursor = connection.cursor()
    cursor.execute("SELECT is_setup FROM powermonitorweb_issetup WHERE id='1'")
    setup = bool(cursor.fetchone()[0])
    if setup:
        return HttpResponseRedirect('/powermonitorweb/')

    if request.method == 'POST':
        setup_homeowner_form = HouseholdSetupUserForm(data=request.POST)

        foods = request.POST.getlist('food_select')
        elec = request.POST['electricity_type']

        if setup_homeowner_form.is_valid:
            homeowner = setup_homeowner_form.save()
            homeowner.set_password(homeowner.password)
            homeowner.is_superuser = True
            homeowner.save()

            cursor.execute("UPDATE powermonitorweb_issetup SET is_setup='1' WHERE id='1'")
            setup = True
        else:
            print setup_homeowner_form.errors
    else:
        setup_homeowner_form = HouseholdSetupUserForm()

    return render_to_response(
        'powermonitorweb/setup_household.html',
        {'setup_homeowner_form': setup_homeowner_form,
         'food_list': food_list,
         'electricity_type': electricity_type,
         'setup': setup},
        context
    )


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
    return render_to_response(
        'powermonitorweb/manage_reports.html',
        {'posted': posted},
        context
    )