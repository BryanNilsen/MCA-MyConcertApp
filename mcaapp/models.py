from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.

class Profile(models.Model):
    ''' extends the User model and adds extra user profile properties '''

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_photo = models.ImageField(upload_to='profile', blank=True)
    quote_lyrics = models.CharField(max_length=100, blank=True)
    favorite_artist = models.CharField(max_length=40, blank=True)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class UserConcert(models.Model):
  ''' joins the user with the concert attended and adds user notes and rating '''

  user = models.ForeignKey(Profile, on_delete=models.CASCADE)
  concert_id = models.CharField(max_length=20)
  notes = models.TextField(max_length=500, blank=True)
  rating = models.IntegerField(
        default=11,
        validators=[MaxValueValidator(11), MinValueValidator(1)]
     )

class UserConcertMedia(models.Model):
  ''' allows users to add multiple photos/videos per concert '''

  user_concert = models.ForeignKey(UserConcert, on_delete=models.CASCADE)
  media = models.ImageField(upload_to='media')
  description = models.CharField(max_length=50, blank=True)
  is_private = models.BooleanField(default=True)