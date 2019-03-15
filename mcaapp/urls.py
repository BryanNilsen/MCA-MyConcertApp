from django.conf.urls import url
from django.urls import path

from . import views

app_name = "mcaapp"
urlpatterns = [
    url(r'^$', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('about/', views.about, name='about'),
    path('faq/', views.faq, name='faq'),
    url(r'^login$', views.login_user, name='login'),
    url(r'^logout$', views.user_logout, name='logout'),
    url(r'^register$', views.register, name='register'),
    url(r'^profile$', views.update_profile, name='profile'),
    url(r'^concerts$', views.concert_list, name='concerts'),
    path('concert_create/', views.concert_create, name='concert_create'),
    path('concert_detail/<int:user_concert_id>/', views.concert_detail, name='concert_detail'),
    path('concert_update/<int:user_concert_id>/', views.concert_update, name='concert_update'),
    path('concert_delete/<int:user_concert_id>/', views.concert_delete, name='concert_delete'),
    path('concert_media/<int:user_concert_id>/', views.concert_media, name='concert_media'),
    path('concert_media_delete/<int:user_concert_media_id>/', views.concert_media_delete, name='concert_media_delete'),
    url(r'^gallery_public$', views.gallery_public, name='gallery_public'),
    url(r'^gallery_user$', views.gallery_user, name='gallery_user'),
]