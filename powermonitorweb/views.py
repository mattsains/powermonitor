from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db import connection
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test

from powermonitorweb.forms import UserForm
from powermonitorweb.forms import HouseholdSetupUserForm, HouseholdSetupFoodsForm, HouseholdElectricityForm

def index(request):
    context = RequestContext(request)
    return render_to_response('powermonitorweb/index.html', {}, context)

def setup_household(request):
    '''
    Setup up the household profile
    REQUIRED:   The database table powermonitorweb_issetup must have data. This should be set up when the system
                is deployed and should not require intervention from the user.
    '''
    context = RequestContext(request)
    cursor = connection.cursor()
    cursor.execute("SELECT is_setup FROM powermonitorweb_issetup WHERE id='1'")
    setup = bool(cursor.fetchone()[0])
    if setup:
        return render_to_response('powermonitorweb/not_admin.html')

    if request.method == 'POST':
        setup_homeowner_form = HouseholdSetupUserForm(data=request.POST)
        setup_food_form = HouseholdSetupFoodsForm(data=request.POST)
        setup_electricity_form = HouseholdElectricityForm(data=request.POST)

        if all([setup_homeowner_form.is_valid, setup_food_form.is_valid,setup_electricity_form.is_valid]):
            homeowner = setup_homeowner_form.save()
            homeowner.set_password(homeowner.password)
            homeowner.is_superuser = True
            homeowner.save()

            setup_food_form.save()
            setup_electricity_form.save()

            cursor.execute("UPDATE powermonitorweb_issetup SET is_setup='1' WHERE id='1'")
        else:
            print setup_homeowner_form.errors, setup_electricity_form.errors
    else:
        setup_homeowner_form = HouseholdSetupUserForm()
        setup_food_form = HouseholdSetupFoodsForm()
        setup_electricity_form = HouseholdElectricityForm()

    return render_to_response(
        'powermonitorweb/setup_household.html',
        {'setup_homeowner_form': setup_homeowner_form,
         'setup_electricity_form': setup_electricity_form,
         'setup_food_form': setup_food_form},
        context
    )

@login_required()
def add_user(request):
    '''
    Add User view.
    Add a new user to the system. Only the homeowner is able to access this.
    '''
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
            if user.is_active:
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

@login_required()
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/powermonitorweb/')