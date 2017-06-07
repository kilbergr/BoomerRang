# -*- coding: utf-8 -*-
from datetime import datetime, timezone
import os
from unittest.mock import patch
from urllib.parse import urljoin, urlencode

from django.core.exceptions import MiddlewareNotUsed
from django.db.utils import IntegrityError
from django.test import Client, RequestFactory, TestCase
from django.utils import timezone
from phonenumber_field.phonenumber import PhoneNumber as ModelPhoneNumber

from boomerrang.boomerrang_app import view_helpers, views
from boomerrang.boomerrang_app.forms import BoomForm
from boomerrang.boomerrang_app.models import Org, CallRequest, Call, PhoneNumber

FAKE_ENV_VAR_DICT = {
    'TWILIO_ACCOUNT_SID': 'hi',
    'TWILIO_AUTH_TOKEN': 'hi',
    'TWILIO_NUMBER': 'hi',
    'CALL_STATUS_URL': 'http://www.boomerrang.com/call-status/',
    'OUTBOUND_URL': 'http://www.boomerrang.com/outbound/'
}

FAKE_INCORRECT_ENV_VAR_DICT = {
    'TWILIO_ACCOUNT_SID': 'hi',
    'TWILIO_AUTH_TOKEN': '',
    'TWILIO_NUMBER': 'hi',
    'CALL_STATUS_URL': 'http://www.boomerrang.com/call-status/',
    'OUTBOUND_URL': 'http://www.boomerrang.com/outbound/',
}

_CALLBACK_STATUS_DICT = {
    'Called': '+15005550006',
    'ToState': 'NY',
    'CallerCountry': 'US',
    'Direction': 'outbound-api',
    'Timestamp': 'Thurs, 20 July 1989 18:30:43 +0000',
    'CallbackSource': 'call-progress-events',
    'CallerState': 'CA',
    'ToZip': '10028',
    'SequenceNumber': '0',
    'CallSid': 'CAf19604a3eec3e63d157870c5f7f3b3a0',
    'To': '+15005550006',
    'CallerZip': '94571',
    'ToCountry': 'US',
    'ApiVersion': '2010-04-01',
    'CalledZip': '10028',
    'CalledCity': 'NEW YORK',
    'CallStatus': 'completed',
    'From': '+15107571675',
    'AccountSid': 'AC8d88ba5085adeac4015ea92ec9a81ded',
    'CalledCountry': 'US',
    'CallerCity': 'SAN FRANCISCO',
    'Caller': '+15107571675',
    'FromCountry': 'US',
    'ToCity': 'NEW YORK',
    'FromCity': 'SAN FRANCISCO',
    'CalledState': 'NY',
    'FromZip': '94571',
    'AnsweredBy': '',
    'FromState': 'CA',
    'CallDuration': ''
}

_OUTBOUND_DICT = {
    'Called': '+15005550006',
    'ToState': 'NY',
    'CallerCountry': 'US',
    'Direction': 'outbound-api',
    'CallerState': 'CA',
    'ToZip': '10028',
    'CallSid': 'CAdfa81b7d24b71e3ec38190794b45011a',
    'To': '+15005550006',
    'CallerZip': '94571',
    'ToCountry': 'US',
    'ApiVersion': '2010-04-01',
    'CalledZip': '10028',
    'CalledCity': 'NEW+YORK',
    'CallStatus': 'in-progress',
    'From': '+15107571675',
    'AccountSid': 'AC8d88ba5085adeac4015ea92ec9a81ded',
    'CalledCountry': 'US',
    'CallerCity': 'SAN+FRANCISCO',
    'Caller': '+15107571675',
    'FromCountry': 'US',
    'ToCity': 'NEW+YORK',
    'FromCity': 'SAN+FRANCISCO',
    'CalledState': 'NY',
    'FromZip': '94571',
    'AnsweredBy': 'human',
    'FromState': 'CA'
}

_BAD_CALLBACK = ('/call-status/3/?Called=+15005550006',
    'ToState=NY&CallerCountry=US&Direction=outbound-api&Timeout')


def _construct_callback_url(id_num, answered_by, duration):
    _CALLBACK_STATUS_DICT['AnsweredBy'] = answered_by
    _CALLBACK_STATUS_DICT['CallDuration'] = duration
    base_url = '/call-status/{}/?'.format(id_num)
    return '{}{}'.format(base_url, urlencode(_CALLBACK_STATUS_DICT))


def _construct_outbound_url(number):
    base_url = '/outbound/{}/?'.format(number)
    return '{}{}'.format(base_url, urlencode(_OUTBOUND_DICT))


def _create_call_req(id_num):
    org = Org.objects.create(username='boblah', password='blah')
    source_num = PhoneNumber.objects.create(
         number=ModelPhoneNumber.from_string('+15105005006'))
    call_req = CallRequest.objects.create(
        source_num=source_num,
        target_num='+15005550006',
        time_scheduled=datetime(1989, 7, 20, 18, 30, 43, tzinfo=timezone.utc),
        org=org,
        call_completed=False,
        id=id_num)
    return call_req


def _create_call_obj(call_req_id, id_num):
    related_cr = CallRequest.objects.get(id=call_req_id)
    call = Call.objects.create(
        call_time=datetime(1989, 7, 20, 18, 30, 43, tzinfo=timezone.utc),
        call_request=related_cr,
        success=None,
        id=id_num)
    return call


class ModelTests(TestCase):

    def setUp(self):
        self.client = Client()

    def test_callrequest_has_org(self):
        # Given: Two org objects
        org = Org.objects.create(username='boblah', password='blah')
        org2 = Org.objects.create(username='org2', password='pw2')
        source_num = PhoneNumber.objects.create(
            number=ModelPhoneNumber.from_string('+15105005000'))

        # And: A call_req with a valid and available twilio number is
        # associated with one of them
        call_req = CallRequest(
            source_num=source_num, target_num='+15005550006', org=org)

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
        source_num = PhoneNumber.objects.create(
            number=ModelPhoneNumber.from_string('+15105005000'))

        # When: CallRequest obj is created with a valid & available twilio
        # number
        call_request = CallRequest(
            source_num=source_num,
            target_num='15005550006',
            time_scheduled=call_time
        )

        # When: Call obj is saved
        with self.assertRaises(Exception):
            # Then: Raise exception when attempting to save call obj
            call_request.save()

    def test_callrequest_must_be_unique(self):
        # Given: A valid CallRequest object
        call_request1 = _create_call_req(1)

        # When: Duplication is attempted
        # Then: Raise exception because unique constraint violated
        with self.assertRaises(IntegrityError):
            call_request2 = _create_call_req(1)


class ViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

    def test_index_response(self):
        # Given: Views
        # When: Home view is visited
        response = self.client.get('/')

        # Then: Expect form in response, and status_code of 200
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)

    def test_form_valid(self):
        # Given: PhoneNumber and date time objects
        source_num = ModelPhoneNumber.from_string('+15105005000')
        target_num = ModelPhoneNumber.from_string('+14155005000')
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
        source_num = ModelPhoneNumber.from_string('+15105005000')
        target_num = ModelPhoneNumber.from_string('+1415500000')
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
        source_num = ModelPhoneNumber.from_string('+15105005000')
        target_num = ModelPhoneNumber.from_string('+14155100000')
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

    def test_valid_form_can_post_and_create_scheduled_call_request(self):
        # Given: valid PhoneNumber and datetime objects
        source_num = ModelPhoneNumber.from_string('+15105005000')
        target_num = ModelPhoneNumber.from_string('+14155005000')
        time_scheduled = datetime.now().strftime('%m-%d-%Y %H:%M')

        page_data = {
            'source_num': source_num,
            'target_num': target_num,
            'time_scheduled': time_scheduled,
            'schedule': 'Schedule Call'
        }

        # When the form is posted to schedule path
        self.client.post('/', data=page_data)
        retrieved_source_num = PhoneNumber.objects.get(
            number=ModelPhoneNumber.from_string('+15105005000'))
        call_req = CallRequest.objects.get(
            source_num=retrieved_source_num,
            target_num='+14155005000',)

        # The resulting call_request object will contain expected data
        self.assertEqual(call_req.source_num, retrieved_source_num)
        self.assertEqual(call_req.target_num, target_num)
        # No calls would have been created
        self.assertEqual(len(Call.objects.all()), 0)

    def test_valid_form_cannot_post_and_create_duplicate_call_request(self):
        # Given: valid PhoneNumber and datetime objects
        source_num = ModelPhoneNumber.from_string('+15105005000')
        target_num = ModelPhoneNumber.from_string('+14155005000')
        time_scheduled = datetime.now().strftime('%m-%d-%Y %H:%M')

        page_data = {
            'source_num': source_num,
            'target_num': target_num,
            'time_scheduled': time_scheduled,
            'schedule': 'Schedule Call'
        }

        # When the form is posted to schedule path
        request1 = self.client.post('/', data=page_data)

        request2 = self.client.post('/', data=page_data)
        self.assertEqual(request1.status_code, 200)
        self.assertEqual(request2.status_code, 302)

    def test_valid_form_can_post_and_create_call_now_request(self):
        # Given: valid PhoneNumber and datetime objects
        source_num = ModelPhoneNumber.from_string('+15105005000')
        target_num = ModelPhoneNumber.from_string('+14155005000')
        time_scheduled = datetime.now().strftime('%m-%d-%Y %H:%M')

        page_data = {
            'source_num': source_num,
            'target_num': target_num,
            'time_scheduled': time_scheduled,
            'callnow': 'Call Now'
        }

        # When the form is posted to schedule path
        self.client.post('/', data=page_data)
        retrieved_source_num = PhoneNumber.objects.get(
            number=ModelPhoneNumber.from_string('+15105005000'))
        call_req = CallRequest.objects.get(
            source_num=retrieved_source_num,
            target_num='+14155005000',)

        # The resulting call_request object will contain expected data
        self.assertEqual(call_req.source_num, retrieved_source_num)
        self.assertEqual(call_req.target_num, target_num)
        # A call would have been created
        self.assertEqual(len(Call.objects.all()), 1)

    @patch.object(view_helpers.Client, 'calls', autospec=True)
    def test_invalid_form_cannot_post_or_create_call_request(self, mock_calls):
        # Given: PhoneNumber and invalid date time objects
        source_num = ModelPhoneNumber.from_string('+15105005000')
        target_num = ModelPhoneNumber.from_string('+14155005000')
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

        source_num_obj = PhoneNumber.objects.create(
            number=ModelPhoneNumber.from_string('+15105005000'))
        call_req = CallRequest.objects.filter(
            source_num=source_num_obj,
            target_num='+14155005000',)
        # And there will be no resulting call_request object
        self.assertEqual(len(call_req), 0)

    @patch.object(views.twiml.Response, 'dial', autospec=True)
    def test_outbound_success_route(self, mock_dial):
        # Given: An request to outbound view
        target_num = '+15105005000'
        outbound_request = _construct_outbound_url(target_num)
        request = self.factory.get(outbound_request)
        # When: A response is given
        response = views.outbound(request, target_num)

        # Then: Expect it to return 200 status code and to call dial once
        self.assertEqual(response.status_code, 200)
        self.assertEqual(mock_dial.call_count, 1)

    @patch.object(views.twiml.Response, 'dial', autospec=True)
    def test_outbound_failure_route(self, mock_dial):
        # Given: A request to outbound view that will throw an Exception
        mock_dial.side_effect = Exception
        target_num = '+15005550001'
        outbound_request = _construct_outbound_url(target_num)
        request = self.factory.get(outbound_request)
        # When: The response is given
        response = views.outbound(request, target_num)

        # Then: Expect to redirect to index when dial is called
        self.assertEqual(response.status_code, 302)
        self.assertEqual(mock_dial.call_count, 1)

    def test_human_answer_updates_call_obj_via_call_status(self):
        # Given: No call objects
        self.assertEqual(len(Call.objects.all()), 0)

        # When: A call request and related call objects are created
        call_req = _create_call_req(1)
        call = _create_call_obj(call_req.id, 1)
        self.assertEqual(call.success, None)

        # And: A request is made to call_status webhook with completed, human answer
        human_answer = _construct_callback_url(call_req.id, 'human', 42)
        request = self.factory.get(human_answer)
        response = views.call_status(request, call_req.id, call.id)

        # Then: There will be a successful Call object and a 200 status code
        self.assertEqual(Call.objects.get(id=call.id).success, True)
        self.assertEqual(response.status_code, 200)

    def test_machine_answer_updates_call_obj_via_call_status(self):
        # Given: No call objects
        self.assertEqual(len(Call.objects.all()), 0)

        # When: A call request and related call objects are created
        call_req = _create_call_req(2)
        call = _create_call_obj(call_req.id, 1)
        self.assertEqual(call.success, None)

        # And: A request is made to call_status webhook with a completed, machine answer
        machine_answer = _construct_callback_url(call_req.id, 'machine', 0)
        request = self.factory.get(machine_answer)
        response = views.call_status(request, call_req.id, call.id)

        # Then: There will be a failed Call object and a 200 status code
        self.assertEqual(Call.objects.get(id=call.id).success, False)
        self.assertEqual(response.status_code, 200)
        # And: Related call_request will have call_completed remaining False
        self.assertFalse(CallRequest.objects.get(id=2).call_completed)

    def test_bad_callback_updates_call_obj_via_call_status(self):
        # Given: No call objects
        self.assertEqual(len(Call.objects.all()), 0)

        # When: A call request and related call objects are created
        call_req = _create_call_req(3)
        call = _create_call_obj(call_req.id, 1)
        self.assertEqual(call.success, None)

        # And: A request is made to the call_status webhook without required information
        request = self.factory.get(_BAD_CALLBACK)
        response = views.call_status(request, call_req.id, call.id)

        # Then: There will be a failed Call object and a 200 status code
        self.assertEqual(Call.objects.get(id=call.id).success, False)
        self.assertEqual(response.status_code, 200)
        # And: Related call_request will have call_completed remaining False
        self.assertFalse(CallRequest.objects.get(id=3).call_completed)


class ViewHelpersTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    @patch.dict(os.environ, FAKE_ENV_VAR_DICT)
    def test_load_twilio_config(self):
        # Given: View_helpers
        # When: Twilio configs are loaded
        config = view_helpers.load_twilio_config()
        # And: only config vars are loaded
        env_vars = tuple(FAKE_ENV_VAR_DICT.values())
        env_vars = tuple(x for x in tuple(
            FAKE_ENV_VAR_DICT.values()) if 'http' not in x)

        # Then: configs conform to expectations
        self.assertEqual(config, env_vars)

    @patch.dict(os.environ, FAKE_INCORRECT_ENV_VAR_DICT)
    def test_load_no_twilio_config_fails(self):
        # Given: View_helpers
        # When: Twilio configs with missing env variables

        # Then: lack of env variables raises MiddlewareNotUsed exception
        with self.assertRaises(MiddlewareNotUsed):
            view_helpers.load_twilio_config()

    @patch.dict(os.environ, FAKE_ENV_VAR_DICT)
    def test_load_twilio_client_success(self):
        # Given: view_helpers and config tuple
        config = view_helpers.load_twilio_config()

        # When: twilio_client is loaded with configs
        twilio_client = view_helpers.load_twilio_client(config[1], config[2])
        # Then: twilio client is based on expected configs
        self.assertEqual(twilio_client.auth, ('hi', 'hi'))

    @patch.object(view_helpers.Client, 'calls', autospec=True)
    @patch.dict(os.environ, FAKE_ENV_VAR_DICT)
    def test_make_call_places_call(self, mock_calls):
        # Given: A call_req with a valid and available twilio number
        call_req = _create_call_req(1)
        call = _create_call_obj(call_req.id, 1)

        # When: make_call is called
        view_helpers.make_call(call_req, call.id)

        # Then: create has been called with expected input
        self.assertEqual(mock_calls.create.call_count, 1)
        # Including the correct forwarding URLs
        outbound_url = urljoin(FAKE_ENV_VAR_DICT['OUTBOUND_URL'], '+15005550006/')
        callstatus_url = urljoin(FAKE_ENV_VAR_DICT['CALL_STATUS_URL'], '{0!s}/{1!s}/'.format(
            call_req.id, call.id))
        mock_calls.create.assert_called_once_with(
            from_=FAKE_ENV_VAR_DICT['TWILIO_NUMBER'],
            to='+15105005006',
            url=outbound_url,
            method='GET',
            status_callback=callstatus_url,
            status_callback_method='POST',
            if_machine='Hangup',)

    def test_record_call_status_success_route(self):
        # Given: a CallRequest object and related call object
        call_req = _create_call_req(1)
        _create_call_obj(1, 1)
        # When: A human answered call's status is recorded

        human_answer = _construct_callback_url(1, 'human', 42)
        request = self.factory.get(human_answer)
        call_status_info = view_helpers._record_call_status(request, call_req)

        # Then: Dictionary will be as expected
        self.assertEqual(call_status_info,
            {'Success': True,
            'CallDuration': '42',
            'CallStatus': 'completed',
            'AnsweredBy': 'human',
            'Timestamp': call_req.time_scheduled
            })

        # And: Related call_request will have call_completed set to True
        self.assertTrue(CallRequest.objects.get(id=1).call_completed)

    def test_record_call_status_machine_answer_route(self):
        # Given: a CallRequest object and related call object
        call_req = _create_call_req(2)
        _create_call_obj(2, 1)

        # When: A machine answered call's status is recorded
        machine_answer = _construct_callback_url(1, 'machine', 0)
        request = self.factory.get(machine_answer)
        call_status_info = view_helpers._record_call_status(request, call_req)

        # Then: Dictionary will be as expected
        self.assertEqual(call_status_info,
            {'Success': False,
            'CallDuration': 0,
            'CallStatus': 'completed',
            'AnsweredBy': 'machine',
            'Timestamp': call_req.time_scheduled
            })

        # And: Related call_request will have call_completed set to True
        self.assertFalse(CallRequest.objects.get(id=2).call_completed)
