from datetime import datetime
from django.test import Client
from django.utils import timezone
import unittest
from unittest.mock import patch

from phonenumber_field.phonenumber import PhoneNumber

from boomerrang.boomerrang_app.models import Org, CallRequest, Call
from boomerrang.boomerrang_app.forms import BoomForm
from boomerrang.boomerrang_app import views
from boomerrang.boomerrang_app import view_helpers


class ModelTests(unittest.TestCase):
    def setUp(self):
        self.client = Client()

    def test_callrequest_has_org(self):
        # Given: Two org objects
        org = Org.objects.create(username='boblah', password='blah')
        org2 = Org.objects.create(username='org2', password='pw2')

        # And: A call_req associated with one of them
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

        # When: CallRequest obj is created
        call_request = CallRequest(
          source_num='15005550006',
          target_num='15005550006',
          time_scheduled=call_time
        )

        # When: Call obj is saved
        with self.assertRaises(Exception):
            # Then: Raise exception when attempting to save call obj
            call_request.save()


class ViewTests(unittest.TestCase):

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
        time_scheduled = datetime.now().strftime('%m-%d-%Y')

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
        time_scheduled = datetime.now().strftime('%m-%d-%Y')

        form_data = {
            'source_num': source_num,
            'target_num': target_num,
            'time_scheduled': time_scheduled,
        }

        # If that data is in a BoomForm
        form = BoomForm(data=form_data)
        # Then the form is valid
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
        # Then the form is valid
        self.assertFalse(form.is_valid())

    @patch.object(view_helpers.Client, 'calls', autospec=True)
    def test_valid_form_can_post_and_create_call_request(self, mock_calls):
      # Given: valid PhoneNumber and datetime objects
        source_num = PhoneNumber.from_string('+15105005000')
        target_num = PhoneNumber.from_string('+14155005000')
        time_scheduled = datetime.now().strftime('%m-%d-%Y')

        form_data = {
            'source_num': source_num,
            'target_num': target_num,
            'time_scheduled': time_scheduled,
        }

        # When the form is posted
        response = self.client.post('/', data=form_data)
        # Then a call will be created
        self.assertEqual(mock_calls.create.call_count, 1)

        call_req = CallRequest.objects.filter(
                      source_num='+15105005000',
                      target_num='+14155005000',)
        # And the resulting call_request object will contain expected data
        self.assertEqual(call_req[0].source_num, source_num)
        self.assertEqual(call_req[0].target_num, target_num)

    @patch.object(view_helpers.Client, 'calls', autospec=True)
    def test_invalid_form_cannot_post_or_create_call_request(self, mock_calls):
      # Given: PhoneNumber and invalid date time objects
        source_num = PhoneNumber.from_string('+15105005000')
        target_num = PhoneNumber.from_string('+14155005000')
        time_scheduled = datetime.now()

        form_data = {
            'source_num': source_num,
            'target_num': target_num,
            'time_scheduled': time_scheduled,
        }

        # When the invalid form is posted
        response = self.client.post('/', data=form_data)
        # Then a call will not be created
        self.assertEqual(mock_calls.create.call_count, 0)

        call_req = CallRequest.objects.filter(
                      source_num='+15105005000',
                      target_num='+14155005000',)
        # And there will be no resulting call_request object
        self.assertEqual(len(call_req), 0)

       # TODO: (Rebecca) Needs views tests that test Twilio


class ViewHelpersTests(unittest.TestCase):

    def test_load_twilio_config(self):
        # Given: View_helpers
        # When: Twilio configs are loaded
        test_num, test_sid, test_token = view_helpers.load_twilio_config()

        # Then: configs conform to expectations
        self.assertEqual(len(test_token), 32)
        self.assertEqual(len(test_sid), 34)
        self.assertIn('+1', test_num)

    @patch.object(view_helpers.Client, 'calls', autospec=True)
    def test_make_calls_places_call(self, mock_calls):
        # Given: A call_req with twilio # +15107571675
        call_time = timezone.now()
        org = Org(username='boblah', password='blah')
        call_req = CallRequest(
            source_num='+15005550006', target_num='+15005550006', org=org)

        # When: make_calls is called
        view_helpers.make_calls(call_req)

        # Then: create has been called with expected input
        self.assertEqual(mock_calls.create.call_count, 1)
        mock_calls.create.assert_called_once_with(
            from_='+15107571675', to='+15005550006', url='+15005550006/')
