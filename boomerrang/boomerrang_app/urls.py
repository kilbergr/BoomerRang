from django.conf.urls import url

from boomerrang.boomerrang_app import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^outbound\/(?P<target_num>\+1[0-9]{10})\/$', views.outbound, name='outbound'),
    url(r'^call-status/$', views.call_status, name='call_status')]
