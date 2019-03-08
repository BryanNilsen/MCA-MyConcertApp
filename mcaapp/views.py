from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import render, reverse
from django.template import RequestContext
from django.contrib import messages
from django.conf import settings
# from django.urls import reverse
import requests

# transaction -> if errors occur, the database is being rolled back
from django.db import transaction

# imported forms
from mcaapp.forms import UserForm
from mcaapp.forms import UserUpdateForm
from mcaapp.forms import ProfileForm
from mcaapp.forms import ConcertSearchForm
from mcaapp.forms import UserConcertForm

#  imported models
from django.contrib.auth.models import User
from mcaapp.models import Profile
from mcaapp.models import UserConcert
from mcaapp.models import UserConcertMedia


# Create your views here


def index(request):
    ''' main landing page for all users / includes search functionality '''

    template_name = 'index.html'



    search_result = {}
    if 'artistName' in request.GET:
        form = ConcertSearchForm(request.GET)
        if form.is_valid():
            search_result = form.search()
    else:
        form = ConcertSearchForm()
    return render(request, template_name, {'form': form, 'search_result': search_result})


@transaction.atomic
# transaction.atomic prevents a partial record being created in the database
def register(request):
    '''Handles the creation of a new user for authentication

    Method arguments:
      request -- The full HTTP request object
    '''
    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    # Create a new user by invoking the `create_user` helper method
    # on Django's built-in User model
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = ProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()
            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()

            file = None
            if "profile_photo" in request.FILES:
                file = request.FILES['profile_photo']

            user.profile.profile_photo = file
            user.profile.quote_lyrics = profile_form.cleaned_data.get('quote_lyrics')
            user.profile.favorite_artist = profile_form.cleaned_data.get('favorite_artist')
            user.profile.save()

            # Update our variable to tell the template registration was successful.
            registered = True


        return login_user(request)

    elif request.method == 'GET':
        user_form = UserForm()
        profile_form = ProfileForm()
        template_name = 'register.html'
        return render(request, template_name, {
          'user_form': user_form,
          'profile_form': profile_form
          })


def update_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        profile = Profile.objects.get(pk=request.user.profile.id)
        print("REQUEST.FILES", request.FILES)
        print("REQUEST.POST", request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.save()
            print("BOTH FORMS ARE VALID")

            # if clear photo checkbox is ticked
            if 'profile_photo-clear' in request.POST:
                print("profile photo was cleared")
                profile.profile_photo.delete()
                profile.profile_photo = None

            # if new file is uploaded, it will delete existing and then add new file
            if 'profile_photo' in request.FILES:
                print("profile photo was uploaded")
                profile.profile_photo.delete()
                file = request.FILES['profile_photo']
                profile.profile_photo = file

            profile.quote_lyrics = request.POST['quote_lyrics']
            profile.favorite_artist = request.POST['favorite_artist']
            profile.save()
            # profile_form.save()

            # messages.success(request, _('Your profile was successfully updated!'))
            return HttpResponseRedirect(reverse('mcaapp:profile'))
        # else:
            # messages.error(request, _('Please correct the error below.'))
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


def login_user(request):
    '''Handles the creation of a new user for authentication

    Method arguments:
      request -- The full HTTP request object
    '''

    # Obtain the context for the user's request.
    context = RequestContext(request)

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':

        # Use the built-in authenticate method to verify
        username=request.POST['username']
        password=request.POST['password']
        authenticated_user = authenticate(username=username, password=password)

        # If authentication was successful, log the user in
        if authenticated_user is not None:
            login(request=request, user=authenticated_user)
            return HttpResponseRedirect('/')

        else:
            # Bad login details were provided. So we can't log the user in.
            print("Invalid login details: {}, {}".format(username, password))
            return HttpResponse("Invalid login details supplied.")


    return render(request, 'login.html', {}, context)

# Use the login_required() decorator to ensure only those logged in can access the view.
@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage. Is there a way to not hard code
    # in the URL in redirects?????
    return HttpResponseRedirect('/')

def get_concert(concert_id):
# API LOGIC HERE to PING API WITH CONCERT ID
    url = 'https://api.setlist.fm/rest/1.0/setlist/{concert_id}'
    headers = {
      'x-api-key': settings.SETLIST_FM_API_KEY,
      'Accept': 'application/json'
      }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:  # SUCCESS
        result = response.json()
        result['success'] = True
    else:
        result['success'] = False
        if response.status_code == 404:  # NOT FOUND
            result['message'] = 'No entry found'
        else:
            result['message'] = 'The Setlist API is not available at the moment. Please try again later.'
    return result


def concert_list(request):
    """lists all current user concerts"""
    user = request.user
    concerts = UserConcert.objects.filter(user_id=user.id)

    for concert in concerts:
        setlistId = concert.concert_id
        endpoint = 'https://api.setlist.fm/rest/1.0/setlist/{setlistId}'
        url = endpoint.format(setlistId=setlistId)
        headers = {
          'x-api-key': settings.SETLIST_FM_API_KEY,
          'Accept': 'application/json'
          }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:  # SUCCESS
            result = response.json()
            result['success'] = True
            # set the api results as a key on the concert object
            concert.api = result

    template_name = 'concerts/list.html'

    return render(request, template_name, {'concerts': concerts})


def concert_create(request):
    ''' adds concert and redirects to update/edit form'''

    if request.method == "POST":
        user = request.user
        concert_id = request.POST['concert_id']
        new_concert = UserConcert(user=user.profile, concert_id=concert_id)
        new_concert.save()
        user_concert_id = new_concert.id

        return HttpResponseRedirect(reverse('mcaapp:concert_update', args=(user_concert_id,)))



def concert_update(request, user_concert_id):
    ''' displays form page and updates user concert details '''

    # get the userconcert to be edited
    template_name = 'concerts/update.html'
    user_concert_to_be_edited = get_object_or_404(UserConcert, pk=user_concert_id)

    # get concert info from API
    # REFACTOR to use GET CONCERT METHOD above TO CALL AND PASS SETLIST ID (concerts.concert_id)
    concerts = UserConcert.objects.get(pk=user_concert_id)
    setlistId = concerts.concert_id
    endpoint = 'https://api.setlist.fm/rest/1.0/setlist/{setlistId}'
    url = endpoint.format(setlistId=setlistId)
    headers = {
      'x-api-key': settings.SETLIST_FM_API_KEY,
      'Accept': 'application/json'
      }
    response = requests.get(url, headers=headers)
    concertApi = response.json()

    if request.method == "GET":
        print("USER CONCERT !!!!!!!!!", user_concert_to_be_edited)
        #No data submitted, create a blank form
        form = UserConcertForm(instance=user_concert_to_be_edited)

    if request.method == "POST":
        print("YOU DID IT!!", user_concert_id)
        updateForm = UserConcertForm(request.POST, instance=user_concert_to_be_edited)
        updateForm.save()

        return HttpResponseRedirect('/concerts')


    return render(request, template_name, {'form': form, 'concert': user_concert_to_be_edited, 'concertApi': concertApi})

def concert_delete(request, user_concert_id):
    concert = UserConcert.objects.get(pk=user_concert_id)
    concert.delete()

    print("you clicked delete for", concert)
    return HttpResponseRedirect('/concerts')

