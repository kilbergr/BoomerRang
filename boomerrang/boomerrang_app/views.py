# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timedelta, timezone

from boomerrang.boomerrang_app import view_helpers
from boomerrang.boomerrang_app.forms import BoomForm
from boomerrang.boomerrang_app.models import (Call, CallRequest, Org,
                                              PhoneNumber)
from django.contrib import messages
from django.db.utils import IntegrityError
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from twilio import twiml

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
            time_scheduled_utc_obj = form.cleaned_data['time_scheduled_utc']

            # Retrieve or create a phone number obj from source_num form
            # information
            (source_num, _) = PhoneNumber.objects.get_or_create(
                number=source_num_obj)

            # Todo (rebecca) should retrieve org object from page info or user
            # info
            fake_org = Org.objects.get_or_create(
                username='mpi', password='truss')[0]
            past_cutoff = time_scheduled_utc_obj - timedelta(hours=12)
            future_cutoff = time_scheduled_utc_obj + timedelta(hours=12)
            existing_requests = CallRequest.objects.filter(
                source_num=source_num,
                target_num=target_num_obj,
                org=fake_org,
                time_scheduled__gte=past_cutoff,
                time_scheduled__lte=future_cutoff
            )

            # Ensure this person is not placing too many calls to the same
            # target in 24 hours.
            if len(existing_requests) < _NUM_ALLOWED_CALLS:

                # Make new call request object
                try:
                    new_call_request = CallRequest.objects.create(
                        source_num=source_num,
                        target_num=target_num_obj,
                        org=fake_org,
                        time_scheduled=time_scheduled_utc_obj,
                        call_completed=False,)
                except IntegrityError as e:
                    err_msg = 'This is a duplicate call request and will not be completed, {}.'
                    log.error(err_msg.format(e))
                    messages.error(request, err_msg)
                    return redirect('index')

                # If user schedules call in the future
                if 'schedule' in request.POST:
                    messages.success(request, 'Call scheduled!')
                    log.info('Scheduled a call between {} and {}'.format(
                        new_call_request.source_num, new_call_request.target_num))

                # If user calls now
                if 'callnow' in request.POST:
                    new_call_request.time_scheduled = datetime.now(
                        timezone.utc)
                    new_call_request.save()
                    view_helpers.launch_call_process(new_call_request)
                    messages.success(request, 'Call incoming!')
                    log.info('Call occurring now between {} and {}'.format(
                        new_call_request.source_num.number, new_call_request.target_num))

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
                     "representative, Senator Feinstein, via Boomerrang.",
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
def call_status(request, call_req_id, call_id):
    # Identify related call_request
    related_cr = CallRequest.objects.get(id=call_req_id)

    try:
        # Gather information about call
        call_status_info = view_helpers._record_call_status(
            request, related_cr)

        # Update the relevant call object recording information
        Call.objects.filter(id=call_id).update(
            call_time=call_status_info['Timestamp'],
            success=call_status_info['Success'],
            duration=call_status_info['CallDuration'])

    except KeyError as e:
        # Update call success to False if fails anywhere in this process
        Call.objects.filter(id=call_id).update(
            success=False)
        log.error('No call status information at this time.')

    return HttpResponse(status=200)
