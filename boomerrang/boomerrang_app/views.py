from django.contrib import messages
from django.core.exceptions import MiddlewareNotUsed
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render

import os
from twilio import twiml
from twilio.rest import Client

from boomerrang.boomerrang_app.forms import BoomForm
# from boomerrang.boomerrang_app.models import CallRequest, Org, Call


def load_twilio_config():
    twilio_account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    twilio_auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    twilio_number = os.environ.get('TWILIO_NUMBER')

    if not all([twilio_account_sid, twilio_auth_token, twilio_number]):
        print('Twilio auth info not configured.')
        raise MiddlewareNotUsed
    return (twilio_number, twilio_account_sid, twilio_auth_token)


def index(request):
    form = BoomForm()
    return render(request, 'form_test.html', {'form': form})


# Voice Request URL
def call(request):
    (twilio_number, twilio_account_sid, twilio_auth_token) = load_twilio_config()
    import ipdb; ipdb.set_trace()
    if request.method == 'POST':
        # Load our Twilio credentials
        (twilio_number, twilio_account_sid, twilio_auth_token) = load_twilio_config()

        # Get phone number we need to call
        form = BoomForm(request.POST)

        # Check for form validity, if form valid
        if form.is_valid():
            phone_number = form.cleaned_data['']
            try:
                twilio_client = Client(twilio_account_sid, twilio_auth_token)
            except Exception as e:
                msg = 'Missing configuration variable: {0}'.format(e)
                messages.error(request, msg)

            try:
                twilio_client.calls.create(from_=twilio_number,
                                           to=phone_number,
                                           url='outbound',
                                           _external=True)
            except Exception as e:
                app.logger.error(e)
                return redirect(request, 'index')

            return messages.success(request, 'Call incoming!')
        else:
            messages.error(request, 'Invalid entry')
            return redirect('index')
    elif request.method == 'GET':
        return render(request, 'index.html')


def outbound(request):
    if request.method == 'POST':
        response = twiml.Response()

        # response.say("Thank you for contacting Boomerrang. If this "
        #              "were in production, we'd dial your intended target.",
        #              voice='alice')

        with response.dial() as dial:
            dial.number("+15102894755")
        return str(response)
