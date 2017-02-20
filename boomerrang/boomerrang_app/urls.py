from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^call/$', views.call),
    url(r'^outbound/$', views.outbound, name='outbound')]
