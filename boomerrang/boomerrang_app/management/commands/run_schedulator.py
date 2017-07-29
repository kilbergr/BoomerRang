# Generates calls from uncompleted prior call_requests
import logging
from datetime import datetime

from boomerrang.boomerrang_app.models import CallRequest
from boomerrang.boomerrang_app.view_helpers import launch_call_process
from django.core.management.base import BaseCommand
from django.db.models import Count

log = logging.getLogger('boom_logger')


class Command(BaseCommand):

    def handle(self, *args, **options):
        """
        Creates calls for all Call Request objects that have fewer than 3
        associated call objects and none of these calls have completed
        successfully.

        If there is an associated call object, a call has been attempted. The call is
        considered a 'success' if the source caller has picked up the phone and is
        considered unsuccessful (call object success value is set to False), if
        it went to voice message or the call did not go through.

        If a call is still in progress while the schedulator runs again, its success
        field hasn't been set to True (set to "None"), and the
        schedulator will not initiate a call.

        """
        # Determine how many calls have been attempted per call_request
        annotation = {'calls_count': Count('calls')}
        # Filter for call_requests scheduled before now with <3 calls attempted
        # Where source_num is validated and not blacklisted
        filters = {'time_scheduled__lt': datetime.utcnow(),
                   'calls_count__lt': 3,
                   'source_num__validated': True,
                   'source_num__blacklisted': False}
        # Exclude call_requests that have call_completed=True
        exclusions = {'call_completed': True}

        requests = CallRequest.objects.annotate(
            **annotation).filter(**filters).exclude(**exclusions)

        has_made_call = False
        for request in requests:
            # TODO: @andie - change 'success' attribute on call object to 'status'
            # in order have more useful values. Success should only be True/False.
            # call.status should be set to something like "in progress" when a
            # call is initiated, so we can explicitly check for it below.

            # If any related calls were successful or are still in progress, skip
            unfailed_calls = [(call.success or call.success is None)
                             for call in request.calls.all()]


            if any(unfailed_calls):
                continue

            launch_call_process(request)

            log.info('A call has been made from {} to {} at the scheduled time of {}.'.format(
                request.source_num.number,
                request.target_num,
                request.time_scheduled
            ))

            has_made_call = True

        # Log if there are no call requests for the period in question
        if not has_made_call:
            info_msg = 'There are no calls to make for this period.'
            log.info(info_msg)
