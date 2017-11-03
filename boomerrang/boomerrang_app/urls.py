from boomerrang.boomerrang_app import views
from django.conf.urls import url

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^outbound\/(?P<target_num>\+1[0-9]{10})\/$',
        views.outbound, name='outbound'),
    url(r'^call-status\/(?P<call_req_id>\d+)\/(?P<call_id>\d+)\/$',
        views.call_status, name='call_status'),
]
