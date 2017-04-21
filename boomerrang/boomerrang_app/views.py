# -*- coding: utf-8 -*-
from django.contrib import messages
from django.core.exceptions import MiddlewareNotUsed
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import logging
import os

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
                twilio_client.calls.create(from_=twilio_number,
                                           to=source_num,
                                           url=os.environ.get('OUTBOUND_URL'))

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
        response.say("Hello, you'll be connected momentarily to your "
                     "representative, Senator Feinstein, via Boomerrang.",
                     voice='alice', language='en-EN')
        log.info('Automated message delivered to source number.')

        with response.dial() as dial:
            target_num = "+15102894755"
            dial.number(target_num)

    except Exception as e:
        log.error('Call unable to connect to target: {}'.format(target_num))
        return redirect('index')

    log.info('Call to {} successful!'.format(target_num))

    return HttpResponse(response)
