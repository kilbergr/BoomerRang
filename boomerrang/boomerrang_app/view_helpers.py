from email.utils import parsedate_to_datetime
import logging
from twilio.rest import Client
from urllib.parse import urljoin

from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed
from django.utils import timezone

from boomerrang.boomerrang_app.models import Call

# Setup logging
log = logging.getLogger('boom_logger')


def load_twilio_config():
    twilio_config = (
        settings.TWILIO_ACCOUNT_SID,
        settings.TWILIO_AUTH_TOKEN,
        settings.TWILIO_NUMBER)

    if not all(twilio_config):
        print('Twilio auth info not configured.')
        raise MiddlewareNotUsed
    return twilio_config


def load_twilio_client(twilio_account_sid, twilio_auth_token):
    # Create Twilio client
    try:
        twilio_client = Client(twilio_account_sid, twilio_auth_token)
        return twilio_client
    except Exception as e:
        log.error(e)


def make_call(call_request, call_id):
    # Load our Twilio credentials
    twilio_number, twilio_account_sid, twilio_auth_token = load_twilio_config()
    # Load Twilio client
    twilio_client = load_twilio_client(twilio_account_sid, twilio_auth_token)

    source_num = '+{}{}'.format(call_request.source_num.number.country_code,
                                call_request.source_num.number.national_number)
    # Needs trailing / for URL
    target_num = '+{}{}/'.format(call_request.target_num.country_code,
                                 call_request.target_num.national_number)

    # Place call, url constructed from env var and target_num var
    twilio_client.calls.create(from_=twilio_number,
                               to=source_num,
                               url=urljoin(settings.OUTBOUND_URL,
                                           target_num),
                               method='GET',
                               status_callback=urljoin(settings.CALL_STATUS_URL,
                                                       '{0!s}/{1!s}/'.format(
                                                           call_request.id, call_id)),
                               status_callback_method='POST',
                               if_machine='Hangup')


def launch_call_process(call_request):
    call = Call.objects.create(
        call_time=timezone.now(),
        call_request=call_request,
        success=None)
    make_call(call_request, call.id)


def _record_call_status(request, related_cr):
    # Create dict to hold information of interest from call status response
    call_status_info = {}

    # Retrieve information we need to determine success of call
    # CallDuration will return the duration in seconds
    status_entries = ['CallStatus', 'Timestamp', 'AnsweredBy']

    for entry in status_entries:
        call_status_info[entry] = request.GET[entry]

    # Set Timestamp entry to datetime obj instead of RFC 2822
    call_status_info['Timestamp'] = parsedate_to_datetime(
        call_status_info['Timestamp'])

    # Check whether call was completed by a human (success metric)
    if (call_status_info['CallStatus'] == 'completed' and
            call_status_info['AnsweredBy'] == 'human'):
        # Save call duration and set related CallRequest.call_completed-True
        call_status_info['CallDuration'] = request.GET['CallDuration']
        call_status_info['Success'] = True
        related_cr.call_completed = True
        related_cr.save()
    else:
        # Save duration=0, log miss, don't change CallRequest.call_completed
        call_status_info['CallDuration'] = 0
        call_status_info['Success'] = False
        err_msg = 'Call ended with {} status, answered by {}'
        log.error(err_msg.format(
            call_status_info['CallStatus'], call_status_info['AnsweredBy']))

    return call_status_info
