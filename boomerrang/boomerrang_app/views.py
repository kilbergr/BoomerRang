from django.shortcuts import render
from django.http import HttpResponse

from boomerrang.boomerrang_app.models import CallRequest, Org, Call


def index(request):
    return HttpResponse("Hello, world. You're at the users index.")