from django.contrib import messages
from django.core.exceptions import MiddlewareNotUsed
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render

import os
from twilio import twiml
from twilio.rest import Client

from boomerrang.boomerrang_app.forms import BoomForm
from boomerrang.boomerrang_app.models import CallRequest, Org, Call


def load_twilio_config():
    twilio_account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    twilio_auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    twilio_number = os.environ.get('TWILIO_NUMBER')

    if not all([twilio_account_sid, twilio_auth_token, twilio_number]):
        print('Twilio auth info not configured.')
        raise MiddlewareNotUsed
    return (twilio_number, twilio_account_sid, twilio_auth_token)


def index(request):
<<<<<<< HEAD
    form = BoomForm()
    return render(request, 'form_test.html', {'form': form})


# Voice Request URL
def call(request):
    (twilio_number, twilio_account_sid, twilio_auth_token) = load_twilio_config()
    import ipdb; ipdb.set_trace()
    # Instantiate form
    form = BoomForm(request.POST or None, initial={'source_num': '+11234567891'})

    if request.method == 'POST':
        # Load our Twilio credentials
        (twilio_number, twilio_account_sid, twilio_auth_token) = load_twilio_config()

        # If form valid, clean data and place call
        if form.is_valid():
            phone_num_obj = form.cleaned_data['source_num']
            source_num = '+{}{}'.format(phone_num_obj.country_code, phone_num_obj.national_number)

            try:
                twilio_client = Client(twilio_account_sid, twilio_auth_token)
            except Exception as e:
                msg = 'Missing configuration variable: {0}'.format(e)
                messages.error(request, msg)

            try:
                twilio_client.calls.create(from_=twilio_number,
                                           to=source_num,
                                           url='http://7220b59f.ngrok.io/outbound/')

            except Exception as e:
                # app.logger.error(e)
                print(e)
                return redirect('index')

            messages.success(request, 'Call incoming!')
            return redirect('outbound')
        else:
            messages.error(request, 'Invalid entry')
            return redirect('index')
    return render(request, 'index.html', {'form': form})


def outbound(request):
    try:
        response = twiml.Response()
        response.say("Thank you for contacting Boomerrang. If this "
                     "were in production, we'd dial your intended target.",
                     voice='alice')
        import ipdb; ipdb.set_trace()
        with response.dial() as dial:
            dial.number("+15102894755")

    except Exception as e:
        # app.logger.error(e)
        print(e)
        return redirect('index')

    return str(response)
