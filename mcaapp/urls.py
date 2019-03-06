from django.conf.urls import url

from . import views

app_name = "mcaapp"
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login$', views.login_user, name='login'),
    url(r'^logout$', views.user_logout, name='logout'),
    url(r'^register$', views.register, name='register'),
    url(r'^profile$', views.update_profile, name='profile'),
    url(r'^concerts$', views.concert_list, name='concerts')
]