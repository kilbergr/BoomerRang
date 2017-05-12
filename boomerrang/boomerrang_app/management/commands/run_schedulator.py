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
        annotation = {'calls_count': Count('calls')}
        filters = {'time_scheduled__lt': timezone.now(), 'calls_count__lt': 3}
        exclusions = {'call_completed': True}
        requests = CallRequest.objects.annotate(
            **annotation).filter(**filters).exclude(**exclusions)

        for request in requests:
            # If any related call objects were successful, skip request
            unfailed_calls = [(call.success or call.success is None)
                              for call in request.calls.all()]
            if any(unfailed_calls):
                continue

            call = Call.objects.create(
                call_time=timezone.now(),
                call_request=request)

            make_call(request)
            call.save()
