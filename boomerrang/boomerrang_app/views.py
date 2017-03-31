# -*- coding: utf-8 -*-

from django.contrib import messages
from django.core.exceptions import MiddlewareNotUsed
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

import os
from twilio import twiml
from twilio.rest import Client

from boomerrang.boomerrang_app.forms import BoomForm


def load_twilio_config():
    twilio_account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    twilio_auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    twilio_number = os.environ.get('TWILIO_NUMBER')

    if not all([twilio_account_sid, twilio_auth_token, twilio_number]):
        print('Twilio auth info not configured.')
        raise MiddlewareNotUsed
    return (twilio_number, twilio_account_sid, twilio_auth_token)


def index(request):
    # Instantiate form
    form = BoomForm(request.POST or None, initial={
                    'source_num': '+15105555555'})

    if request.method == 'POST':
        # Load our Twilio credentials
        (twilio_number, twilio_account_sid,
         twilio_auth_token) = load_twilio_config()

        # If form valid, clean data and place call
        if form.is_valid():
            phone_num_obj = form.cleaned_data['source_num']
            source_num = '+{}{}'.format(phone_num_obj.country_code,
                                        phone_num_obj.national_number)

            try:
                twilio_client = Client(twilio_account_sid, twilio_auth_token)
            except Exception as e:
                # TODO (rebecca): Set up logging
                # app.logger.error(e)
                print(e)

            try:
                outbound_url = 'http://polar-wave-91710.herokuapp.com/outbound'
                twilio_client.calls.create(from_=twilio_number,
                                           to=source_num,
                                           url=outbound_url)

            except Exception as e:
                # TODO (rebecca): Set up logging
                # app.logger.error(e)
                print(e)
                return redirect('index')

            messages.success(request, 'Call incoming!')
        else:
            messages.error(request, 'Invalid entry')
    return render(request, 'index.html', {'form': form})


@csrf_exempt
def outbound(request):
    print('Reached outbound')
    try:
        response = twiml.Response()
        response.say("Gracias por contactar con Boomerrang. Estamos "
                     "conectandote con vuestra representativa, Señor Bob.",
                     voice='alice', language='es-ES')

        with response.dial() as dial:
            dial.number("+15102894755")

    except Exception as e:
        # TODO (rebecca): Set up logging
        # app.logger.error(e)
        print(e)
        return redirect('index')

    return HttpResponse(response)
