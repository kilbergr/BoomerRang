# -*- coding: utf-8 -*-
from datetime import timedelta, datetime, timezone
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from email.utils import parsedate_to_datetime
import logging

from twilio import twiml

from boomerrang.boomerrang_app.forms import BoomForm
from boomerrang.boomerrang_app.models import CallRequest, Org
from boomerrang.boomerrang_app import view_helpers

# Setup logging
log = logging.getLogger('boom_logger')
# Magic constants
_NUM_ALLOWED_CALLS = 10


def index(request):
    # Instantiate form
    form = BoomForm(request.POST or None)

    if request.method == 'POST':
        # If form valid, clean data and place call
        if form.is_valid():
            # Clean objects
            source_num_obj = form.cleaned_data['source_num']
            target_num_obj = form.cleaned_data['target_num']
            time_scheduled_obj = form.cleaned_data['time_scheduled']

            # Todo (rebecca) should retrieve org object from page info or user
            # info
            fake_org = Org.objects.get_or_create(
                username='mpi', password='truss')[0]
            past_cutoff = time_scheduled_obj - timedelta(hours=12)
            future_cutoff = time_scheduled_obj + timedelta(hours=12)
            existing_requests = CallRequest.objects.filter(
                source_num=source_num_obj,
                target_num=target_num_obj,
                org=fake_org,
                time_scheduled__gte=past_cutoff,
                time_scheduled__lte=future_cutoff
            )

            # Ensure this person is not placing too many calls to the same
            # target in 24 hours.
            if len(existing_requests) < _NUM_ALLOWED_CALLS:
                # Make new call request object
                new_call_request = CallRequest.objects.create(
                    source_num=source_num_obj,
                    target_num=target_num_obj,
                    org=fake_org,
                    time_scheduled=time_scheduled_obj,
                    call_completed=False,)

                if 'schedule' in request.POST:
                    # If user schedules call in the future
                    messages.success(request, 'Call scheduled!')
                    log.info('Scheduled a call between {} and {}'.format(
                        new_call_request.source_num, new_call_request.target_num))

                if 'callnow' in request.POST:
                    # If user calls now
                    new_call_request.time_scheduled = datetime.now(timezone.utc)
                    new_call_request.save()
                    view_helpers.launch_call_process(new_call_request)
                    messages.success(request, 'Call incoming!')
                    log.info('Call occurring now between {} and {}'.format(
                        new_call_request.source_num, new_call_request.target_num))

            else:
                messages.error(
                    request,
                    'You are placing too many calls during this period.')
        else:
            messages.error(request, 'Invalid entry: {}'.format(form.errors))
    return render(request, 'index.html', {'form': form})


@csrf_exempt
def outbound(request, target_num):
    try:
        response = twiml.Response()
        response.say("Hello, you'll be connected momentarily to your "
                     "representative, Senator Feinstein, via Boomerrang. "
                     "Bai Felicia.",
                     voice='alice', language='en-EN')
        log.info('Automated message delivered to source number.')

        with response.dial() as dial:
            dial.number(target_num)

    except Exception as e:
        log.error('Call unable to connect to target: {}'.format(target_num))
        return redirect('index')

    log.info('Call to {} successful!'.format(target_num))

    return HttpResponse(response)


@csrf_exempt
def call_status(request, call_req_id):
    # Create dict to hold information of interest from call status response
    call_status_info = {}

    # Retrieve information we need to determine success of call
    # CallStatus will be 'completed', 'in-progress', or 'failed'
    # CallDuration will return the duration in seconds
    # Timestamp will return time call was made in RFC 2822
    status_entries = ['CallStatus', 'CallDuration', 'Timestamp']
    for entry in status_entries:
        call_status_info[entry] = request.GET[entry]

    # Set Timestamp entry to datetime obj instead of RFC 2822
    call_status_info['Timestamp'] = parsedate_to_datetime(call_status_info['Timestamp'])

    # Identify related call_request
    related_cr = CallRequest.objects.get(id=call_req_id)

    # Check whether call was successful, set CallRequest.call_completed to True if so
    if call_status_info['CallStatus']=='completed':
        success = True
        related_cr.call_completed = True
    else:
        success = False

    new_call_obj = Call.objects.create(call_time=call_status_info['Timestamp'],
                               success=success,
                               duration=call_status_info['CallDuration'],
                               call_request=related_cr,)
