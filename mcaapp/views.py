from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
import requests

# transaction -> if errors occur, the database is being rolled back
from django.db import transaction

from mcaapp.forms import UserForm, ProfileForm
from mcaapp.models import Profile
# from mcaap.forms import ProductForm


# Create your views here

def index(request):
    template_name = 'index.html'
    return render(request, template_name, {})


@transaction.atomic
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

            user.profile.profile_photo = profile_form.cleaned_data.get('profile_photo')
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
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, _('Your profile was successfully updated!'))
            return redirect('settings:profile')
        else:
            messages.error(request, _('Please correct the error below.'))
    else:
        user_form = UserForm(instance=request.user)
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


# def sell_product(request):
#     if request.method == 'GET':
#         product_form = ProductForm()
#         template_name = 'product/create.html'
#         return render(request, template_name, {'product_form': product_form})

#     elif request.method == 'POST':
#         form_data = request.POST

#         p = Product(
#             seller = request.user,
#             title = form_data['title'],
#             description = form_data['description'],
#             price = form_data['price'],
#             quantity = form_data['quantity'],
#         )
#         p.save()
#         template_name = 'product/success.html'
#         return render(request, template_name, {})

# def list_products(request):
#     all_products = Product.objects.all()
#     template_name = 'product/list.html'
#     return render(request, template_name, {'products': all_products})


# @login_required
# def search_results(request):

#     template_name = 'search/search_results.html'

#     query = request.GET.get('q', '')
#     if query:
#         # query example
#         results = Product.objects.filter(title__icontains=query).distinct()
#     else:
#         results = []
#     return render(request, template_name, {'results': results, 'query': query})



def search(request):
    user = {}
    if 'username' in request.GET:
        username = request.GET['username']
        url = 'https://api.github.com/users/%s' % username
        response = requests.get(url)
        user = response.json()
    return render(request, 'search/search_results.html', {'user': user})