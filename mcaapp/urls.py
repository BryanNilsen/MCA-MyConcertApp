from django.conf.urls import url
from django.urls import path

from . import views

app_name = "mcaapp"
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login$', views.login_user, name='login'),
    url(r'^logout$', views.user_logout, name='logout'),
    url(r'^register$', views.register, name='register'),
    url(r'^profile$', views.update_profile, name='profile'),
    url(r'^concerts$', views.concert_list, name='concerts'),
    path('concert_create/', views.concert_create, name='concert_create'),
    path('concert_update/<int:user_concert_id>/', views.concert_update, name='concert_update'),
    path('concert_delete/<int:user_concert_id>/', views.concert_delete, name='concert_delete'),
]