# -*- coding: utf-8 -*-
from django.contrib import messages
from django.core.exceptions import MiddlewareNotUsed
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import logging

from twilio import twiml
from twilio.rest import Client

from boomerrang.boomerrang_app.forms import BoomForm
from boomerrang.boomerrang_app.models import CallRequest, Org, Call
from boomerrang.boomerrang_app import view_helpers

# Setup logging
log = logging.getLogger('boom_logger')

def index(request):
    # Instantiate form
    form = BoomForm(request.POST or None, initial={
                    'source_num': '+15105555555'})

    if request.method == 'POST':
        # Load our Twilio credentials
        (twilio_number, twilio_account_sid,
         twilio_auth_token) = view_helpers.load_twilio_config()

        # If form valid, clean data and place call
        if form.is_valid():
            phone_num_obj = form.cleaned_data['source_num']
            source_num = '+{}{}'.format(phone_num_obj.country_code,
                                        phone_num_obj.national_number)

            try:
                twilio_client = Client(twilio_account_sid, twilio_auth_token)
            except Exception as e:
                log.error(e)

            try:
                outbound_url = 'http://polar-wave-91710.herokuapp.com/outbound/'
                twilio_client.calls.create(from_=twilio_number,
                                           to=source_num,
                                           url=outbound_url)

            except Exception as e:
                log.error('Call unable to be initiated to source: {}, {}'.format(source_num, e))
                return redirect('index')

            messages.success(request, 'Call incoming!')
            log.info('Call initiated to source - {}'.format(source_num))
        else:
            messages.error(request, 'Invalid entry')
    return render(request, 'index.html', {'form': form})


@csrf_exempt
def outbound(request):
    try:
        response = twiml.Response()
        response.say("Gracias por contactar con Boomerrang. Estamos "
                     "conectandote con vuestra representativa, Senor Bob.",
                     voice='alice', language='es-ES')
        log.info('Automated message delivered to source number.')
        with response.dial() as dial:
            target_num = "+15102894755"
            dial.number(target_num)

    except Exception as e:
        log.error('Call unable to connect to target: {}'.format(target_num))
        return redirect('index')

    log.info('Call from {} to {} successful!'.format(source_num, target_num))

    return HttpResponse(response)
