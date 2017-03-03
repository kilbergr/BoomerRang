from django.shortcuts import render

from boomerrang.boomerrang_app.forms import BoomForm
# from boomerrang.boomerrang_app.models import CallRequest, Org, Call


def index(request):
    form = BoomForm()
    return render(request, 'form_test.html', {'form': form})
