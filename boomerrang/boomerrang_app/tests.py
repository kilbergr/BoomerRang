# -*- coding: utf-8 -*-
from datetime import datetime
import os
from unittest.mock import patch
from urllib.parse import urljoin

import django
from django.core.exceptions import MiddlewareNotUsed
from django.db.utils import IntegrityError
from django.test import Client
from django.utils import timezone
from phonenumber_field.phonenumber import PhoneNumber

from boomerrang.boomerrang_app.models import Org, CallRequest, Call
from boomerrang.boomerrang_app.forms import BoomForm
from boomerrang.boomerrang_app import view_helpers


FAKE_TWILIO_CONFIG_DICT = {
    'TWILIO_ACCOUNT_SID': 'hi',
    'TWILIO_AUTH_TOKEN': 'hi',
    'TWILIO_NUMBER': 'hi'
}

FAKE_EMPTY_TWILIO_CONFIG_DICT = {
    'TWILIO_ACCOUNT_SID': 'hi',
    'TWILIO_AUTH_TOKEN': '',
    'TWILIO_NUMBER': 'hi'
}

FAKE_ENV_URLS = {
    'CALL_STATUS_URL': 'http://www.boomerrang.com/call-status/',
    'OUTBOUND_URL': 'http://www.boomerrang.com/outbound/',
}


class ModelTests(django.test.TestCase):

    def setUp(self):
        self.client = Client()

    def test_callrequest_has_org(self):
        # Given: Two org objects
        org = Org.objects.create(username='boblah', password='blah')
        org2 = Org.objects.create(username='org2', password='pw2')

        # And: A call_req with a valid and available twilio number is
        # associated with one of them
        call_req = CallRequest(
            source_num='+15005550006', target_num='+15005550006', org=org)

        # When: Call_req obj is examined
        # Then: Expected org should be on call_request obj
        self.assertEqual(call_req.org, org)
        self.assertNotEqual(call_req.org, org2)

    def test_call_must_have_callrequest_to_save(self):
        # Given: A call object without a CallRequest
        call_time = timezone.now()
        # When: Call obj is created
        call = Call(call_time=call_time)

        # When: Call obj is saved
        with self.assertRaises(Exception):
            # Then: Raise exception when attempting to save call obj
            call.save()

    def test_callrequest_must_have_org_to_save(self):
        # Given: A CallRequest object without an Org
        call_time = timezone.now()

        # When: CallRequest obj is created with a valid & available twilio
        # number
        call_request = CallRequest(
            source_num='15005550006',
            target_num='15005550006',
            time_scheduled=call_time
        )

        # When: Call obj is saved
        with self.assertRaises(Exception):
            # Then: Raise exception when attempting to save call obj
            call_request.save()

    def test_callrequest_must_be_unique(self):
        # Given: A valid CallRequest object
        org = Org.objects.create(username='boblah', password='blah')
        call_time = timezone.now()
        call_request1 = CallRequest.objects.create(
            source_num='15005550006',
            target_num='15005550006',
            org=org,
            time_scheduled=call_time,
            call_completed=False
        )

        # When: A duplicate is created
        # Then: Raise exception because unique constraint violated
        with self.assertRaises(IntegrityError):
            call_request2 = CallRequest.objects.create(
                source_num='15005550006',
                target_num='15005550006',
                org=org,
                time_scheduled=call_time,
                call_completed=False
            )



class ViewTests(django.test.TestCase):

    def setUp(self):
        self.client = Client()

    def test_index_response(self):
        # Given: Views
        # When: Home view is visited
        response = self.client.get('/')

        # Then: Expect form in response, and status_code of 200
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)

    def test_form_valid(self):
        # Given: PhoneNumber and date time objects
        source_num = PhoneNumber.from_string('+15105005000')
        target_num = PhoneNumber.from_string('+14155005000')
        time_scheduled = datetime.now().strftime('%m-%d-%Y %H:%M')

        form_data = {
            'source_num': source_num,
            'target_num': target_num,
            'time_scheduled': time_scheduled,
        }

        # If that data is in a BoomForm
        form = BoomForm(data=form_data)
        # Then the form is valid
        self.assertTrue(form.is_valid())

    def test_invalid_phone_number_yields_invalid_form(self):
        # Given: Invalid PhoneNumber and date time objects
        source_num = PhoneNumber.from_string('+15105005000')
        target_num = PhoneNumber.from_string('+1415500000')
        time_scheduled = datetime.now().strftime('%m-%d-%Y %H:%M')

        form_data = {
            'source_num': source_num,
            'target_num': target_num,
            'time_scheduled': time_scheduled,
        }

        # If that data is in a BoomForm
        form = BoomForm(data=form_data)
        # Then the form is invalid
        self.assertFalse(form.is_valid())

    def test_invalid_datetime_yields_invalid_form(self):
        # Given: PhoneNumber and invalid datetime objects
        source_num = PhoneNumber.from_string('+15105005000')
        target_num = PhoneNumber.from_string('+14155100000')
        time_scheduled = datetime.now().strftime('%Y-%m-%d')

        form_data = {
            'source_num': source_num,
            'target_num': target_num,
            'time_scheduled': time_scheduled,
        }

        # If that data is in a BoomForm
        form = BoomForm(data=form_data)
        # Then the form is invalid
        self.assertFalse(form.is_valid())

    @patch.object(view_helpers.Client, 'calls', autospec=True)
    def test_valid_form_can_post_and_create_scheduled_call_request(self, mock_calls):
        # Given: valid PhoneNumber and datetime objects
        source_num = PhoneNumber.from_string('+15105005000')
        target_num = PhoneNumber.from_string('+14155005000')
        time_scheduled = datetime.now().strftime('%m-%d-%Y %H:%M')

        page_data = {
            'source_num': source_num,
            'target_num': target_num,
            'time_scheduled': time_scheduled,
            'schedule': 'Schedule Call'
        }

        # When the form is posted to schedule path
        self.client.post('/', data=page_data)

        call_req = CallRequest.objects.get(
            source_num='+15105005000',
            target_num='+14155005000',)

        # The resulting call_request object will contain expected data
        self.assertEqual(call_req.source_num, source_num)
        self.assertEqual(call_req.target_num, target_num)
        # No calls would have been created
        self.assertEqual(len(Call.objects.all()), 0)

    @patch.object(view_helpers.Client, 'calls', autospec=True)
    def test_valid_form_can_post_and_create_call_now_request(self, mock_calls):
        # Given: valid PhoneNumber and datetime objects
        source_num = PhoneNumber.from_string('+15105005000')
        target_num = PhoneNumber.from_string('+14155005000')
        time_scheduled = datetime.now().strftime('%m-%d-%Y %H:%M')

        page_data = {
            'source_num': source_num,
            'target_num': target_num,
            'time_scheduled': time_scheduled,
            'callnow': 'Call Now'
        }

        # When the form is posted to schedule path
        self.client.post('/', data=page_data)

        call_req = CallRequest.objects.get(
            source_num='+15105005000',
            target_num='+14155005000',)

        # The resulting call_request object will contain expected data
        self.assertEqual(call_req.source_num, source_num)
        self.assertEqual(call_req.target_num, target_num)
        # A call would have been created
        self.assertEqual(len(Call.objects.all()), 1)

    @patch.object(view_helpers.Client, 'calls', autospec=True)
    def test_invalid_form_cannot_post_or_create_call_request(self, mock_calls):
        # Given: PhoneNumber and invalid date time objects
        source_num = PhoneNumber.from_string('+15105005000')
        target_num = PhoneNumber.from_string('+14155005000')
        time_scheduled = datetime.now()

        page_data = {
            'source_num': source_num,
            'target_num': target_num,
            'time_scheduled': time_scheduled,
            'schedule': 'Schedule Call'
        }

        # When the invalid form is posted
        self.client.post('/', data=page_data)
        # Then a call will not be created
        self.assertEqual(mock_calls.create.call_count, 0)

        call_req = CallRequest.objects.filter(
            source_num='+15105005000',
            target_num='+14155005000',)
        # And there will be no resulting call_request object
        self.assertEqual(len(call_req), 0)

    @patch.object(view_helpers.Client, 'calls', autospec=True)
    def test_unsuccessful_call_raises_exception(self, mock_calls):
        # Given: A call_req with a valid and available twilio number
        time_scheduled = datetime.now().strftime('%m-%d-%Y')
        org = Org(username='boblah', password='blah')
        call_req = CallRequest(
            source_num='+15005550006', target_num='+15005550006',
            time_scheduled=time_scheduled, org=org)

        # And: A mock that will fail when creating a call
        mock_calls.create.side_effect = Exception('Error raised')

        # When: make_call is called
        # Then: An Exception will be raised
        with self.assertRaises(Exception):
            view_helpers.make_call(call_req)



class ViewHelpersTests(django.test.TestCase):

    @patch.dict(os.environ, FAKE_TWILIO_CONFIG_DICT)
    def test_load_twilio_config(self):
        # Given: View_helpers
        # When: Twilio configs are loaded
        config = view_helpers.load_twilio_config()

        # Then: configs conform to expectations
        self.assertEqual(config, tuple(FAKE_TWILIO_CONFIG_DICT.values()))

    @patch.dict(os.environ, FAKE_EMPTY_TWILIO_CONFIG_DICT)
    def test_load_no_twilio_config_fails(self):
        # Given: View_helpers
        # When: Twilio configs with missing env variables

        # Then: lack of env variables raises MiddlewareNotUsed exception
        with self.assertRaises(MiddlewareNotUsed):
            view_helpers.load_twilio_config()

    @patch.object(view_helpers.Client, 'calls', autospec=True)
    @patch.dict(os.environ, FAKE_TWILIO_CONFIG_DICT)
    @patch.dict(os.environ, FAKE_ENV_URLS)
    def test_make_call_places_call(self, mock_calls):
        # Given: A call_req with a valid and available twilio number
        time_scheduled = datetime.now().strftime('%m-%d-%Y %H:%M')
        org = Org(username='boblah', password='blah')
        call_req = CallRequest(
            source_num='+15005550006', target_num='+15005550006',
            time_scheduled=time_scheduled, org=org)

        # When: make_call is called
        view_helpers.make_call(call_req)

        # Then: create has been called with expected input
        self.assertEqual(mock_calls.create.call_count, 1)
        # Including the correct forwarding URLs
        outbound_url = urljoin(FAKE_ENV_URLS['OUTBOUND_URL'], '+15005550006/')
        callstatus_url = urljoin(FAKE_ENV_URLS['CALL_STATUS_URL'], str(call_req.id))
        mock_calls.create.assert_called_once_with(
            from_=FAKE_TWILIO_CONFIG_DICT['TWILIO_NUMBER'],
            to='+15005550006',
            url=outbound_url,
            method='GET',
            status_callback=callstatus_url,
            status_callback_method='POST',
            if_machine='Hangup')
