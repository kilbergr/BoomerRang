# -*- coding: utf-8 -*-
import datetime
import os
from unittest.mock import patch

import django
from django.core.management import call_command
from django.utils import timezone

from boomerrang.boomerrang_app.models import CallRequest, Org, Call, PhoneNumber
from boomerrang.boomerrang_app import view_helpers


FAKE_TWILIO_CONFIG_DICT = {
    'TWILIO_ACCOUNT_SID': 'hi',
    'TWILIO_AUTH_TOKEN': 'hi',
    'TWILIO_NUMBER': 'hi'
}


class RunSchedulatorTests(django.test.TestCase):

    def setUp(self):
        self.client_patch = patch.object(
            view_helpers.Client, 'calls', autospec=True)
        self.client_patch.start()
        self.addCleanup(self.client_patch.stop)

        self.environ_patch = patch.dict(os.environ, FAKE_TWILIO_CONFIG_DICT)
        self.environ_patch.start()
        self.addCleanup(self.environ_patch.stop)

    def test_schedulator_creates_call_object(self):
        # Given: A CallRequest with time_scheduled <= now
        org = Org(username='boblah', password='blah')
        org.save()
        source_num = PhoneNumber.objects.create(number='+15555555555')
        CallRequest.objects.create(
            source_num=source_num,
            target_num='+15555555555',
            org=org,
            time_scheduled=timezone.now()).save()

        # When: Schedulator 9000 is run
        call_command('run_schedulator')

        calls = Call.objects.all()
        # Then: A call object has been created
        self.assertEqual(len(calls), 1)

    def test_schedulator_does_not_trigger_future_calls(self):
        # Given: A CallRequest with time_scheduled in the future
        org = Org(username='boblah', password='blah')
        org.save()
        source_num = PhoneNumber.objects.create(number='+15555555555')
        future_time = timezone.now() + datetime.timedelta(minutes=10)
        CallRequest.objects.create(
            source_num=source_num,
            target_num='+15555555555',
            org=org,
            time_scheduled=future_time).save()

        # When: Schedulator 9000 is run
        call_command('run_schedulator')

        calls = Call.objects.all()
        # Then: No calls are returned
        self.assertEqual(len(calls), 0)

    def test_schedulator_does_not_retry_completed_call_requests(self):
        # Given: A CallRequest with call_completed set to True
        org = Org(username='boblah', password='blah')
        org.save()
        source_num = PhoneNumber.objects.create(number='+15555555555')
        CallRequest.objects.create(
            source_num=source_num,
            target_num='+15555555555',
            org=org,
            time_scheduled=timezone.now(),
            call_completed=True).save()

        # When: Schedulator 9000 is run
        call_command('run_schedulator')

        calls = Call.objects.all()
        # Then: No calls are created
        self.assertEqual(len(calls), 0)

    def test_schedulator_does_not_retry_successful_calls(self):
        # Given: A CallRequest and a successful call
        org = Org(username='boblah', password='blah')
        org.save()
        source_num = PhoneNumber.objects.create(number='+15555555555')
        request = CallRequest.objects.create(
            source_num=source_num,
            target_num='+15555555555',
            org=org,
            time_scheduled=timezone.now())
        request.save()
        Call.objects.create(
            call_time=timezone.now(),
            success=True,
            duration=42,
            call_request=request).save()

        # When: Schedulator 9000 is run
        call_command('run_schedulator')

        calls = Call.objects.all()
        # Then: No additional calls are created
        self.assertEqual(len(calls), 1)

    def test_schedulator_does_attempt_calling_more_than_thrice(self):
        # Given: A CallRequest and three failed calls
        org = Org(username='boblah', password='blah')
        org.save()
        source_num = PhoneNumber.objects.create(number='+15555555555')
        request = CallRequest.objects.create(
            source_num=source_num,
            target_num='+15555555555',
            org=org,
            time_scheduled=timezone.now())
        request.save()
        for _ in range(0, 3):
            Call.objects.create(
                call_time=timezone.now(),
                success=False,
                duration=42,
                call_request=request).save()

        # When: Schedulator 9000 is run
        call_command('run_schedulator')

        calls = Call.objects.all()
        # Then: No additional calls are created
        self.assertEqual(len(calls), 3)

    def test_schedulator_does_not_retry_unfailed_calls(self):
        # Given: A CallRequest and a yet uncompleted call
        org = Org(username='boblah', password='blah')
        org.save()
        source_num = PhoneNumber.objects.create(number='+15555555555')
        request = CallRequest.objects.create(
            source_num=source_num,
            target_num='+15555555555',
            org=org,
            time_scheduled=timezone.now())
        request.save()
        Call.objects.create(
            call_time=timezone.now(),
            success=None,
            duration=None,
            call_request=request).save()

        # When: Schedulator 9000 is run
        call_command('run_schedulator')

        calls = Call.objects.all()
        # Then: No additional calls are created
        self.assertEqual(len(calls), 1)
