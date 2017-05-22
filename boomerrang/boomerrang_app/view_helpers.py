<<<<<<< HEAD
=======
from django.core.exceptions import MiddlewareNotUsed
>>>>>>> tests for call_status route and call obj creation
from email.utils import parsedate_to_datetime
import logging
import os
from twilio.rest import Client
from urllib.parse import urljoin

from django.core.exceptions import MiddlewareNotUsed
from django.utils import timezone

from boomerrang.boomerrang_app.models import Call

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


def make_call(call_request, call_id):
    # Load our Twilio credentials
    twilio_number, twilio_account_sid, twilio_auth_token = load_twilio_config()
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

    # Place call, url constructed from env var and target_num var
    twilio_client.calls.create(from_=twilio_number,
                               to=source_num,
                               url=urljoin(os.environ.get('OUTBOUND_URL'),
                                  target_num),
                               method='GET',
                               status_callback=urljoin(os.environ.get('CALL_STATUS_URL'),
                                                       '{0!s}/{1!s}'.format(
                                                            call_request.id, call_id)),
                               status_callback_method='POST',
                               if_machine='Hangup')


def launch_call_process(call_request):
    call = Call.objects.create(
        call_time=timezone.now(),
        call_request=call_request,
        success=None)
    make_call(call_request)


def _record_call_status(request, related_cr):
    # Create dict to hold information of interest from call status response
    call_status_info = {}

    # Retrieve information we need to determine success of call
    # CallDuration will return the duration in seconds
    status_entries = ['CallStatus', 'Timestamp', 'AnsweredBy']

    for entry in status_entries:
        call_status_info[entry] = request.GET[entry]

    # Set Timestamp entry to datetime obj instead of RFC 2822
    call_status_info['Timestamp'] = parsedate_to_datetime(call_status_info['Timestamp'])

    # Check whether call was completed by a human (success metric)
    if call_status_info['CallStatus'] == 'completed' and call_status_info['AnsweredBy'] == 'human':
        # Save call duration and set the related CallRequest.call_completed to True if so
        call_status_info['CallDuration'] = request.GET['CallDuration']
        call_status_info['Success'] = True
        related_cr.call_completed = True
        related_cr.save()
    else:
        # Save call duration as 0 and log miss, do not change related CallRequest's call_completed
        call_status_info['CallDuration'] = 0
        call_status_info['Success'] = False
        err_msg = 'Call ended with {} status, answered by {}'
        log.error(err_msg.format(call_status_info['CallStatus'], call_status_info['AnsweredBy']))

    return call_status_info
