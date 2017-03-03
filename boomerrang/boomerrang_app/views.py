from django.shortcuts import render
from django.http import HttpResponse

from boomerrang.boomerrang_app.models import CallRequest, Org, Call 

# Create your views here.


def index(request):
    import pdb
    pdb.set_trace()
    return HttpResponse("Hello, world. You're at the users index.")