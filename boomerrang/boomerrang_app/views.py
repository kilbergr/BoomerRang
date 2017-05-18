# -*- coding: utf-8 -*-
from datetime import timedelta
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
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

                messages.success(request, 'Call scheduled!')
                log.info('Scheduled a call between {} and {}'.format(
                    new_call_request.source_num, new_call_request.target_num))
                # Scheduler runs here, determines which calls to make
                # try:
                #     view_helpers.make_call(new_call_request)
                #     messages.success(request, 'Call incoming!')
                #     log.info('Call initiated to source - {}'.format(
                #         new_call_request.source_num))

                # except Exception as e:
                #     err_msg = 'Call unable to be initiated to source: {}, {}'
                #     log.error(err_msg.format(new_call_request.source_num, e))
                #     return redirect('index')
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
