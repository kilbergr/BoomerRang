# -*- coding: utf-8 -*-
import datetime
from unittest.mock import patch

import django
from boomerrang.boomerrang_app import view_helpers
from boomerrang.boomerrang_app.models import (Call, CallRequest, Org,
                                              PhoneNumber)
from django.core.management import call_command
from django.test.utils import override_settings
from django.utils import timezone

FAKE_TWILIO_CONFIG_DICT = {
    'TWILIO_ACCOUNT_SID': 'hi',
    'TWILIO_AUTH_TOKEN': 'hi',
    'TWILIO_NUMBER': 'hi'
}


@override_settings(**FAKE_TWILIO_CONFIG_DICT)
class RunSchedulatorTests(django.test.TestCase):

    def setUp(self):
        self.client_patch = patch.object(
            view_helpers.Client, 'calls', autospec=True)
        self.client_patch.start()
        self.addCleanup(self.client_patch.stop)

    def test_schedulator_creates_call_object(self):
        # Given: A CallRequest with time_scheduled <= now
        org = Org.objects.create(username='boblah', password='blah')
        source_num = PhoneNumber.objects.create(number='+15555555555',
                                                validated=True)
        CallRequest.objects.create(
            source_num=source_num,
            target_num='+15555555555',
            org=org,
            time_scheduled=timezone.now())

        # When: Schedulator 9000 is run
        call_command('run_schedulator')

        calls = Call.objects.all()
        # Then: A call object has been created
        self.assertEqual(len(calls), 1)

    # TODO: Add back in once validator is included
    # def test_schedulator_invalid_sourcenum_does_not_create_call_object(self):
    #     # Given: A CallRequest with time_scheduled <= now
    #     org = Org.objects.create(username='boblah', password='blah')
    #     source_num = PhoneNumber.objects.create(number='+15555555555',
    #                                             validated=False)
    #     CallRequest.objects.create(
    #         source_num=source_num,
    #         target_num='+15555555555',
    #         org=org,
    #         time_scheduled=timezone.now())

    #     # When: Schedulator 9000 is run
    #     call_command('run_schedulator')

    #     calls = Call.objects.all()
    #     # Then: A call object has been created
    #     self.assertEqual(len(calls), 0)

    def test_schedulator_blacklisted_sourcenum_does_not_create_call_obj(self):
        # Given: A CallRequest with time_scheduled <= now
        org = Org.objects.create(username='boblah', password='blah')
        source_num = PhoneNumber.objects.create(number='+15555555555',
                                                validated=True,
                                                blacklisted=True)
        CallRequest.objects.create(
            source_num=source_num,
            target_num='+15555555555',
            org=org,
            time_scheduled=timezone.now())

        # When: Schedulator 9000 is run
        call_command('run_schedulator')

        calls = Call.objects.all()
        # Then: A call object has been created
        self.assertEqual(len(calls), 0)

    def test_schedulator_does_not_trigger_future_calls(self):
        # Given: A CallRequest with time_scheduled in the future
        org = Org.objects.create(username='boblah', password='blah')
        source_num = PhoneNumber.objects.create(number='+15555555555',
                                                validated=True)
        future_time = timezone.now() + datetime.timedelta(minutes=10)
        CallRequest.objects.create(
            source_num=source_num,
            target_num='+15555555555',
            org=org,
            time_scheduled=future_time)

        # When: Schedulator 9000 is run
        call_command('run_schedulator')

        calls = Call.objects.all()
        # Then: No calls are returned
        self.assertEqual(len(calls), 0)

    def test_schedulator_does_not_retry_completed_call_requests(self):
        # Given: A CallRequest with call_completed set to True
        org = Org.objects.create(username='boblah', password='blah')
        source_num = PhoneNumber.objects.create(number='+15555555555',
                                                validated=True)
        CallRequest.objects.create(
            source_num=source_num,
            target_num='+15555555555',
            org=org,
            time_scheduled=timezone.now(),
            call_completed=True)

        # When: Schedulator 9000 is run
        call_command('run_schedulator')

        calls = Call.objects.all()
        # Then: No calls are created
        self.assertEqual(len(calls), 0)

    def test_schedulator_does_not_retry_successful_calls(self):
        # Given: A CallRequest and a successful call
        org = Org.objects.create(username='boblah', password='blah')
        source_num = PhoneNumber.objects.create(number='+15555555555',
                                                validated=True)
        request = CallRequest.objects.create(
            source_num=source_num,
            target_num='+15555555555',
            org=org,
            time_scheduled=timezone.now())
        Call.objects.create(
            call_time=timezone.now(),
            success=True,
            duration=42,
            call_request=request)

        # When: Schedulator 9000 is run
        call_command('run_schedulator')

        calls = Call.objects.all()
        # Then: No additional calls are created
        self.assertEqual(len(calls), 1)

    def test_schedulator_does_attempt_calling_more_than_thrice(self):
        # Given: A CallRequest and three failed calls
        org = Org.objects.create(username='boblah', password='blah')
        source_num = PhoneNumber.objects.create(number='+15555555555',
                                                validated=True)
        request = CallRequest.objects.create(
            source_num=source_num,
            target_num='+15555555555',
            org=org,
            time_scheduled=timezone.now())
        for _ in range(0, 3):
            Call.objects.create(
                call_time=timezone.now(),
                success=False,
                duration=42,
                call_request=request)

        # When: Schedulator 9000 is run
        call_command('run_schedulator')

        calls = Call.objects.all()
        # Then: No additional calls are created
        self.assertEqual(len(calls), 3)

    def test_schedulator_does_not_retry_unfailed_calls(self):
        # Given: A CallRequest and a yet uncompleted call
        org = Org.objects.create(username='boblah', password='blah')
        source_num = PhoneNumber.objects.create(number='+15555555555',
                                                validated=True)
        request = CallRequest.objects.create(
            source_num=source_num,
            target_num='+15555555555',
            org=org,
            time_scheduled=timezone.now())
        Call.objects.create(
            call_time=timezone.now(),
            success=None,
            duration=None,
            call_request=request)

        # When: Schedulator 9000 is run
        call_command('run_schedulator')

        calls = Call.objects.all()
        # Then: No additional calls are created
        self.assertEqual(len(calls), 1)
