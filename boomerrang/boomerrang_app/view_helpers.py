from django.contrib import messages
from django.shortcuts import redirect
import logging
import os
from urllib.parse import urljoin

from twilio.rest import Client


# Setup logging
log = logging.getLogger('boom_logger')


def load_twilio_config():
    twilio_account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    twilio_auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    twilio_number = os.environ.get('TWILIO_NUMBER')

    if not all([twilio_account_sid, twilio_auth_token, twilio_number]):
        print('Twilio auth info not configured.')
        raise MiddlewareNotUsed
    return (twilio_number, twilio_account_sid, twilio_auth_token)


def make_calls(call_request):
     # Load our Twilio credentials
    (twilio_number, twilio_account_sid,
    twilio_auth_token) = load_twilio_config()
    # Create Twilio client
    try:
        twilio_client = Client(twilio_account_sid, twilio_auth_token)
    except Exception as e:
        log.error(e)

    source_num = '+{}{}'.format(call_request.source_num.country_code,
                                call_request.source_num.national_number)
    # Needs trailing / for URL
    target_num = '+{}{}/'.format(call_request.target_num.country_code,
                                call_request.target_num.national_number)

    # Place calls, url constructed from env var and target_num var
    try:
        twilio_client.calls.create(from_=twilio_number,
                                   to=source_num,
                                   url=urljoin(os.environ.get('OUTBOUND_URL'),
                                               target_num))

    except Exception as e:
        log.error('Call unable to be initiated to source: {}, {}'.format(
            call_request.source_num, e))
        return redirect('index')
