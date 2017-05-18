# Generates calls from uncompleted prior call_requests
import logging

from django.db.models import Count
from django.core.management.base import BaseCommand
from django.utils import timezone

from boomerrang.boomerrang_app.models import CallRequest, Call
from boomerrang.boomerrang_app.view_helpers import make_call

log = logging.getLogger('boom_logger')


class Command(BaseCommand):

    def handle(self, *args, **options):
        # Determine how many calls have been attempted per call_request
        annotation = {'calls_count': Count('calls')}
        # Filter for call_requests scheduled before now with fewer than 3 calls attempted
        filters = {'time_scheduled__lt': timezone.now(), 'calls_count__lt': 3}
        # Exclude call_requests that have call_completed=True
        exclusions = {'call_completed': True}
        requests = CallRequest.objects.annotate(
            **annotation).filter(**filters).exclude(**exclusions)

        # Log if there are no call requests for the period in question
        if len(requests)==0:
            info_msg = 'There are no calls to make for this period.'
            log.info(info_msg)

        for request in requests:
            # If any related calls were successful or are still in progress, skip
            unfailed_calls = [(call.success or call.success is None)
                              for call in request.calls.all()]
            if any(unfailed_calls):
                info_msg = 'This call request has calls that were successful or are currently in progress.'
                log.info(info_msg)
                continue

            call = Call.objects.create(
                call_time=timezone.now(),
                call_request=request,
                success=True)

            make_call(request)
            call.save()
            info_msg = 'A call has been made via the schedulator.'
            log.info(info_msg)
