from django.contrib.auth.models import User
from django import forms
from mcaapp.models import Profile
from mcaapp.models import UserConcert
from mcaapp.models import UserConcertMedia
from django.conf import settings

import requests

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name')

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

class ProfileForm(forms.ModelForm):
    class Meta:
      model = Profile
      fields = ('profile_photo', 'quote_lyrics', 'favorite_artist')

class UserConcertForm(forms.ModelForm):
    class Meta:
      model = UserConcert
      fields = ('notes', 'rating')

class ConcertSearchForm(forms.Form):
    artistName = forms.CharField(max_length=100, label='Artist')
    venueName = forms.CharField(max_length=100, required=False, label='Location (venue, city, or state)')

    def search(self):
        result = {}
        artistName = self.cleaned_data['artistName']
        venueName = self.cleaned_data['venueName']
        endpoint = 'https://api.setlist.fm/rest/1.0/search/setlists?artistName={artistName}&venueName={venueName}'
        url = endpoint.format(artistName=artistName, venueName=venueName)
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
                result['message'] = 'No entry found for this search of "%s"' % artistName
            else:
                result['message'] = 'The Setlist API is not available at the moment. Please try again later.'
        return result

class UserConcertMediaForm(forms.ModelForm):
    class Meta:
      model = UserConcertMedia
      fields = ('media', 'description', 'is_private')