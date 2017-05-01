from django.conf.urls import url

from boomerrang.boomerrang_app import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^outbound\/$', views.outbound, name='outbound')]
